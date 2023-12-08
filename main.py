# server for adbshot, listen on 5650 at path GET /screen for sending screenshot

import os
import sys

def log(s: str):
    print(s)
    sys.stdout.flush()

import signal
def terminate(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGTERM, terminate)

log("[+] configuring adbshot...")
HOME = os.getenv('HOME', '/adb')
ADB_HOME = os.path.join(HOME, '.android')
LISTEN_PORT = os.getenv('LISTEN_PORT', '5650')

log(f"[+] configuring adb...")
ADB_HOST = os.getenv('ADB_HOST', '10.1.1.132')
ADB_PORT = os.getenv('ADB_PORT', '5555')
ADB_PRIVATE_KEY = os.getenv('ADB_PRIVATE_KEY', '/data/adbkey')
ADB_PUBLIC_KEY = os.getenv('ADB_PUBLIC_KEY', '/data/adbkey.pub')

log(f"[+] setting up adb server secrets...")
os.system(f"rm -rf {ADB_HOME}")
os.mkdir(ADB_HOME)
os.system(f"cp {ADB_PRIVATE_KEY} {ADB_HOME}/")
os.system(f"cp {ADB_PUBLIC_KEY} {ADB_HOME}/")

def adb_heart_beat():
    print(f"[+] checking connection to adb server {ADB_HOST}:{ADB_PORT}...")
    check_resp = os.system(f"adb connect {ADB_HOST}:{ADB_PORT}")
    if check_resp != 0:
        raise Exception("[-] unable to connect to adb server")
    resp = os.popen(f"adb -s {ADB_HOST}:{ADB_PORT} shell echo 'Hello World'").read()
    if resp.strip() != "Hello World":
        raise Exception("[-] unable to connect to adb server")
    return

from flask import Flask, send_file
app = Flask(__name__)

import datetime
log("[+] starting adbshot server...")

@app.route('/health')
def health():
    try:
        adb_heart_beat()
    except Exception as e:
        return str(e), 503
    return "OK", 200

@app.route('/capture')
def screen():
    try:
        adb_heart_beat()
    except Exception as e:
        return str(e), 503
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    uuid = os.urandom(4).hex()
    filename = f"/tmp/screen-{timestamp}-{uuid}.png"
    print(f"[+] saving screenshot to {filename}")
    if os.path.exists(filename): os.remove(filename)

    os.system(f"adb -s {ADB_HOST}:{ADB_PORT} exec-out screencap -p > {filename}")
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return "[-] unable to capture screenshot", 503

    data = send_file(filename, mimetype='image/png')
    os.remove(filename)

    return data

# if __name__ == "__main__":
# fuck you production WSGI server
log(f"[+] listening on port {LISTEN_PORT}")
app.run(host='0.0.0.0', port=LISTEN_PORT)
