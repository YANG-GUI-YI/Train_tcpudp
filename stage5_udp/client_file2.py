
import socket
import struct
import json
import hashlib
import time
from pathlib import Path

SERVER_IP = "192.168.56.1"
PORT = 5001
CHUNK_SIZE = 1024
MAX_FILE_SIZE = 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "test.txt"

file_size = FILE_PATH.stat().st_size

if file_size > MAX_FILE_SIZE:
    raise ValueError("測試檔案超過 1 MiB")

file_hash = hashlib.sha256(FILE_PATH.read_bytes()).hexdigest()
total_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE

metadata = {
    "name": FILE_PATH.name,
    "size": file_size,
    "chunks": total_chunks,
    "sha256": file_hash
}

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:

    target = (SERVER_IP, PORT)

    # 1. START：傳送檔案資訊
    start_data = json.dumps(metadata).encode("utf-8")
    client.sendto(b"S" + start_data, target)

    print("檔名：", FILE_PATH.name)
    print("總區塊數：", total_chunks)

    time.sleep(0.1)

    # 2. DATA：分塊傳送
    with open(FILE_PATH, "rb") as file:
        seq = 0

        while True:
            chunk = file.read(CHUNK_SIZE)

            if not chunk:
                break

            # Type: D (1 Byte)
            # Sequence: 4 Bytes
            header = struct.pack("!cI", b"D", seq)
            if seq == 2:
                # 模擬丟包，跳過傳送 Chunk 2
                print(f"模擬丟包，跳過 Chunk 2")
            else:
                client.sendto(header + chunk, target)

            print(f"傳送 Chunk {seq}, {len(chunk)} Bytes")

            seq += 1
            time.sleep(0.005)

    # 3. END：傳送結束標記
    client.sendto(b"E", target)

    print("全部資料報已送出")
