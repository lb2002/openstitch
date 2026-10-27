"""Melco NetBridge – WLAN-Brücke für USB-Disketten-Emulatoren (GoTek / FlashFloppy) an der EMT10/4.

Läuft auf einem Raspberry Pi Zero 2 W (ca. 18 €), der im USB-Gadget-Modus (`g_mass_storage`)
als USB-Stick im GoTek-Laufwerk der Melco EMT10/4 steckt.

Funktion:
- Stellt im lokalen WLAN einen kleinen HTTP-Server (Port 8070) bereit.
- OpenStitch (oder jeder Browser) kann `.EXP`-Dateien oder komplette `1.44 MB .IMG`-Diskettenabbilder
  per Klick an `http://<pi-ip>:8070/upload` senden.
- Der Server legt die Datei im gemeinsamen USB-Image ab und aktualisiert den USB-Massenspeicher,
  sodass das Design sofort im Bedienfeld der Melco EMT10/4 erscheint – ganz ohne USB-Stick-Umstecken!
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

STORAGE_DIR = os.environ.get("MELCO_STORAGE_DIR", "./melco_usb_root")


class BridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        files = sorted(os.listdir(STORAGE_DIR))
        body = json.dumps({"status": "ok", "machine": "Melco EMT10/4 NetBridge", "files": files}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        length = int(self.headers.get("Content-Length", "0"))
        fname = os.path.basename(self.headers.get("X-Filename", "DESIGN.EXP"))
        data = self.rfile.read(length)
        target = os.path.join(STORAGE_DIR, fname)
        with open(target, "wb") as f:
            f.write(data)
        os.sync() if hasattr(os, "sync") else None

        # Falls ein Linux USB-Gadget-Backing-Image aktiv ist, Dateisystem-Cache flushen
        gadget_reload = os.environ.get("MELCO_GADGET_RELOAD_CMD")
        if gadget_reload:
            subprocess.run(gadget_reload, shell=True, check=False)

        resp = json.dumps({"saved": fname, "bytes": len(data)}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)


def main():
    ap = argparse.ArgumentParser(description="Melco EMT10/4 WLAN-USB-Brücke")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8070)
    ap.add_argument("--dir", default=STORAGE_DIR, help="Zielverzeichnis / gemountetes USB-Image")
    args = ap.parse_args()
    global STORAGE_DIR
    STORAGE_DIR = args.dir
    os.makedirs(STORAGE_DIR, exist_ok=True)
    print(f"Melco NetBridge aktiv auf http://{args.host}:{args.port} -> {os.path.abspath(STORAGE_DIR)}")
    HTTPServer((args.host, args.port), BridgeHandler).serve_forever()


if __name__ == "__main__":
    main()
