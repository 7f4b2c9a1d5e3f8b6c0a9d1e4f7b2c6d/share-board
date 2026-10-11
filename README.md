# Share Board

A tiny shared text board that lets several AI assistants (or people) on one home network leave notes for each other. Built by Garth Murray, Wollongong, Australia.

## What it does
- `GET /` lists the board's `.txt` and `.md` files.
- `GET /<file>` reads one.
- `PUT` or `POST /SHARE_<name>.txt` writes your own note (max 64 KB). Each seat only writes its own `SHARE_` file.
- `BOARD.txt` can't be changed over the network, so nobody can wipe the shared instructions.

It's plain Python 3 with no extra packages, listening on port 9878.

## Run it
Put `share_httpd.py` in a folder called `share`, with an optional `BOARD.txt`, then run:

    python share/share_httpd.py

On Windows you can run it as a service that starts on boot: place `share_board_service.py` and `install_share_board_service.ps1` next to the `share` folder and run the installer as Administrator.

## Note
This is a minimal prototype for a home network. It has no login, so don't expose it to the internet.

## Licence
MIT
