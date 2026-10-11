"""Windows service wrapper for share_httpd.py.
Runs the board with no console window and logs next to this file.
Set SHARE_DIR below to the folder holding share_httpd.py and the board files.
Install with install_share_board_service.ps1 (run as Administrator)."""
import logging, os, sys, threading
import servicemanager, win32event, win32service, win32serviceutil

HERE = os.path.dirname(os.path.abspath(__file__))
SHARE_DIR = os.path.join(HERE, "share")
LOG = os.path.join(HERE, "share_board_service.log")
sys.path.insert(0, SHARE_DIR)

logging.basicConfig(filename=LOG, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

class ShareBoardService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ShareBoard9878"
    _svc_display_name_ = "Share Board (port 9878)"
    _svc_description_ = "Runs share_httpd.py, a small shared text board, on port 9878."

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.server = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.server:
            self.server.shutdown()
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        import share_httpd as board
        from http.server import ThreadingHTTPServer
        os.chdir(SHARE_DIR)
        ThreadingHTTPServer.allow_reuse_address = True
        self.server = ThreadingHTTPServer((board.HOST, board.PORT), board.Handler)
        log = logging.getLogger("board")
        board.Handler.log_message = lambda h, fmt, *a: log.info("%s - %s", h.address_string(), fmt % a)
        logging.info("share board started on %s:%s", board.HOST, board.PORT)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
        logging.info("share board stopped")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ShareBoardService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ShareBoardService)
