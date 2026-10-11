# Run in an Administrator PowerShell from this folder.
# Installs the share board as a Windows service that starts on boot and restarts if it crashes.
$py = (Get-Command python).Source
& $py -m pip install pywin32
& $py "$PSScriptRoot\share_board_service.py" --startup auto install
sc.exe failure ShareBoard9878 reset= 86400 actions= restart/5000/restart/5000/restart/30000
Start-Service ShareBoard9878
Get-Service ShareBoard9878
