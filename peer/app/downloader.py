import os
import socket
import threading
import time
from typing import List, Dict
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn
import requests

TRACKER_URL = "http://tracker:9000/api/v1"
MAX_RETRIES = 3
CHUNK_BUFFER_SIZE = 64 * 1024  # 64KB per read


def fetch_chunk(ip: str, port: int, filename: str, idx: int, start: int, end: int, progress_task, progress, results):
    """Download a chunk from a peer using raw TCP socket, with retries."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.sendall(f"{filename}:{start}:{end}\n".encode())

            buffer = bytearray()
            while len(buffer) < end - start:
                data = s.recv(CHUNK_BUFFER_SIZE)
                if not data:
                    break
                buffer.extend(data)
                progress.update(progress_task, advance=len(data))
            s.close()

            if len(buffer) != end - start:
                raise ValueError(f"Expected {end-start} bytes, got {len(buffer)} bytes")

            results[idx] = {
                "chunk_id": idx,
                "peer": f"{ip}:{port}",
                "size": len(buffer),
                "data": bytes(buffer)
            }
            return  # success
        except Exception as e:
            print(f"Chunk {idx} from {ip}:{port} failed (attempt {attempt}/{MAX_RETRIES}): {e}")
            time.sleep(1)  # short delay before retry
    print(f"Chunk {idx} from {ip}:{port} permanently failed.")
    results[idx] = None


def download_file(filename: str, total_size: int, peers: List[Dict], save_folder: str, self_ip: str, self_port: int):
    """Download file from multiple peers using threads, merge chunks, notify tracker."""
    os.makedirs(save_folder, exist_ok=True)
    save_path = os.path.join(save_folder, filename)
    with open(save_path, "wb") as f:
        pass

    num_peers = len(peers)
    chunk_size = total_size // num_peers
    results = [None] * num_peers

    progress = Progress(
        TextColumn("[bold blue]{task.fields[filename]}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>6.2f}%",
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    )

    start_time = time.perf_counter()

    with progress:
        task_id = progress.add_task("download", filename=filename, total=total_size)
        threads = []

        for i, peer in enumerate(peers):
            start = i * chunk_size
            end = total_size if i == num_peers - 1 else (i + 1) * chunk_size
            t = threading.Thread(
                target=fetch_chunk,
                args=(peer["ip"], peer["port"], filename, i, start, end, task_id, progress, results)
            )
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    with open(save_path, "wb") as out:
        for r in sorted(filter(None, results), key=lambda x: x["chunk_id"]):
            out.write(r["data"])
            elapsed = time.perf_counter() - start_time
            print(f"✔ Chunk {r['chunk_id']} downloaded from {r['peer']} ({r['size']} bytes) in {elapsed:.2f}s")

    try:
        res = requests.post(f"{TRACKER_URL}/complete", json={
            "peer_ip": self_ip,
            "port": self_port,
            "name": filename
        })
        if res.status_code == 200:
            return res.json()
        else:
            print(f"Tracker returned status code {res.status_code}")
            return {}
    except Exception as e:
        print(f"Notify tracker failed: {e}")
        return {}