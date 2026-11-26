
import socket
import json
import hashlib
import struct
from pathlib import Path

SERVER = ("192.168.56.1", 5001)
CHUNK_SIZE = 1024
MAX_FILE_SIZE = 1024 * 1024
TIMEOUT = 1
MAX_RETRIES = 5

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "test.txt"

START_ACK = b"A" + struct.pack("!I", 0xFFFFFFFF)


def send_with_ack(sock, packet, expected_ack):
    for attempt in range(1, MAX_RETRIES + 1):

        # 第一次故意不傳送 DATA Seq 2
        if packet[:5] == b"D" + (2).to_bytes(4, "big") and attempt == 1:
            print("模擬遺失 DATA Seq 2")
        else:
            sock.sendto(packet, SERVER)

        try:
            while True:
                response, addr = sock.recvfrom(4096)

                if addr != SERVER:
                    continue

                if response == b"X":
                    raise RuntimeError("Server 拒絕傳輸")

                if response == expected_ack:
                    return

        except socket.timeout:
            print(f"第 {attempt} 次等待逾時，準備重傳")

    raise TimeoutError("重試次數已達上限")


file_data = FILE_PATH.read_bytes()

if len(file_data) > MAX_FILE_SIZE:
    raise ValueError("檔案超過 1 MiB")

total_chunks = (
    len(file_data) + CHUNK_SIZE - 1
) // CHUNK_SIZE

metadata = {
    "name": FILE_PATH.name,
    "size": len(file_data),
    "chunks": total_chunks,
    "sha256": hashlib.sha256(file_data).hexdigest()
}

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
    client.settimeout(TIMEOUT)

    # 1. START
    start = b"S" + json.dumps(
        metadata, ensure_ascii=False
    ).encode("utf-8")

    send_with_ack(client, start, START_ACK)
    print("START 已確認")

    # 2. DATA
    for seq in range(total_chunks):
        offset = seq * CHUNK_SIZE
        chunk = file_data[offset:offset + CHUNK_SIZE]

        packet = struct.pack("!cI", b"D", seq) + chunk
        ack = struct.pack("!cI", b"A", seq)

        send_with_ack(client, packet, ack)
        print(f"Chunk {seq} 已確認")

    # 3. END
    send_with_ack(client, b"E", b"F")

    print("Server 已確認檔案完整")
    print("UDP 檔案傳輸成功")
