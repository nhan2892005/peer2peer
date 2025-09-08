import os
import socket
import threading
from datetime import datetime


def peer_server(port: int, folder: str):
    def handle_client(conn, addr):
        try:
            request = conn.recv(1024).decode().strip()
            filename, start, end = request.split(":")
            start, end = int(start), int(end)

            fpath = os.path.join(folder, filename)
            with open(fpath, "rb") as f:
                f.seek(start)
                remaining = end - start
                while remaining > 0:
                    data = f.read(min(64 * 1024, remaining))
                    if not data:
                        break
                    conn.sendall(data)
                    remaining -= len(data)

            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"[{addr}] Sent {filename} {start}:{end}")
        except Exception as e:
            print("Error:", e)
        finally:
            conn.close()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        s.listen()
        print(f"Peer listening on {port}, sharing {folder}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()