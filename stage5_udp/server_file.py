
import socket
import json
import hashlib
from pathlib import Path

HOST = "192.168.56.1"
PORT = 5001
CHUNK_SIZE = 1024
MAX_FILE_SIZE = 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
SAVE_DIR = BASE_DIR / "received_files"
SAVE_DIR.mkdir(exist_ok=True)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
    server.bind((HOST, PORT))
    server.settimeout(15)

    print("等待 UDP START 資料報...")

    # 1. 接收 START
    while True:
        packet, client_addr = server.recvfrom(4096)

        if packet[:1] == b"S":
            break

    metadata = json.loads(packet[1:].decode("utf-8"))

    file_name = metadata["name"]
    file_size = metadata["size"]
    total_chunks = metadata["chunks"]
    expected_hash = metadata["sha256"]

    # 檢查檔案資訊
    if (
        not isinstance(file_name, str)
        or not file_name
        or file_name in (".", "..")
        or any(c in file_name for c in '/\\:')
        or file_name.endswith((".", " "))
        or any(ord(c) < 32 for c in file_name)
    ):
        raise ValueError("不合法的檔名")

    if (
        type(file_size) is not int
        or not 0 <= file_size <= MAX_FILE_SIZE
        or type(total_chunks) is not int
        or total_chunks !=
            (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
    ):
        raise ValueError("檔案大小或區塊數不合法")

    if (
        not isinstance(expected_hash, str)
        or len(expected_hash) != 64
        or any(c not in "0123456789abcdef"
               for c in expected_hash)
    ):
        raise ValueError("不合法的 SHA-256")

    print("準備接收：", file_name)
    print("預期區塊：", total_chunks)

    chunks = {}
    end_received = False
    server.settimeout(3)

    # 2. 接收 DATA / END
    try:
        while not (end_received and
                   len(chunks) == total_chunks):

            packet, addr = server.recvfrom(4096)

            if addr != client_addr or not packet:
                continue

            if packet[:1] == b"E":
                end_received = True
                continue

            if packet[:1] != b"D" or len(packet) < 5:
                continue

            seq = int.from_bytes(packet[1:5], "big")
            payload = packet[5:]

            if seq >= total_chunks:
                continue

            expected_len = min(
                CHUNK_SIZE,
                file_size - seq * CHUNK_SIZE
            )

            if len(payload) != expected_len:
                continue

            chunks[seq] = payload
            print(f"收到 Chunk {seq}")

    except socket.timeout:
        print("等待資料報逾時")

    # 3. 檢查資料是否完整
    missing = [
        i for i in range(total_chunks)
        if i not in chunks
    ]

    if missing or not end_received:
        print("檔案接收不完整")
        print("缺少 Chunk：", missing)
        print("是否收到 END：", end_received)

    else:
        # 依照序號重新組合
        content = b"".join(
            chunks[i] for i in range(total_chunks)
        )

        actual_hash = hashlib.sha256(content).hexdigest()

        if actual_hash != expected_hash:
            print("SHA-256 驗證失敗")
        else:
            save_path = SAVE_DIR / ("received_" + file_name)

            # 避免覆蓋已存在的檔案
            with open(save_path, "xb") as file:
                file.write(content)

            print("檔案重組成功！")
            print("儲存位置：", save_path)
            print("SHA-256 驗證成功")
