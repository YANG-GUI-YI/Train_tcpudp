
import socket
import json
import hashlib
import struct
import time
from pathlib import Path

HOST = "192.168.56.1"
PORT = 5001
CHUNK_SIZE = 1024
MAX_FILE_SIZE = 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
SAVE_DIR = BASE_DIR / "received_files"
SAVE_DIR.mkdir(exist_ok=True)

START_ACK = b"A" + struct.pack("!I", 0xFFFFFFFF)

# 修改為 True，可以模擬 ACK 遺失
DROP_ACK_ONCE = True
dropped = False

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
    server.bind((HOST, PORT))
    server.settimeout(15)

    print("等待 UDP START...")

    # 1. 接收 START
    while True:
        packet, client_addr = server.recvfrom(4096)

        if packet[:1] == b"S":
            try:
                metadata = json.loads(packet[1:].decode("utf-8"))

                name = metadata["name"]
                size = metadata["size"]
                count = metadata["chunks"]
                expected_hash = metadata["sha256"]

                valid_name = (
                    isinstance(name, str)
                    and 0 < len(name.encode("utf-8")) <= 200
                    and name not in (".", "..")
                    and not any(c in name for c in '/\\:')
                    and not name.endswith((".", " "))
                    and not any(ord(c) < 32 for c in name)
                )

                valid = (
                    valid_name
                    and type(size) is int
                    and 0 <= size <= MAX_FILE_SIZE
                    and type(count) is int
                    and count == (size + CHUNK_SIZE - 1) // CHUNK_SIZE
                    and isinstance(expected_hash, str)
                    and len(expected_hash) == 64
                    and all(c in "0123456789abcdef"
                            for c in expected_hash)
                )

                if not valid:
                    raise ValueError("檔案資訊不合法")

            except (ValueError, KeyError, TypeError, UnicodeError):
                server.sendto(b"X", client_addr)
                continue

            server.sendto(START_ACK, client_addr)
            break

    print("準備接收：", name)
    print("總 Chunk 數：", count)

    chunks = {}
    server.settimeout(10)

    # 2. 接收 DATA
    # Stop-and-Wait：只接收預期的序號
    expected_seq = 0

    while expected_seq < count:
        packet, addr = server.recvfrom(4096)

        if addr != client_addr:
            continue

        # START ACK 遺失時，Client 會重傳 START
        if packet == b"S" + json.dumps(
            metadata, ensure_ascii=False
        ).encode("utf-8"):
            server.sendto(START_ACK, client_addr)
            continue

        if len(packet) < 5 or packet[:1] != b"D":
            continue

        seq = int.from_bytes(packet[1:5], "big")
        payload = packet[5:]

        if seq == expected_seq:
            expected_len = min(
                CHUNK_SIZE, size - seq * CHUNK_SIZE
            )

            if len(payload) != expected_len:
                continue

            chunks[seq] = payload
            expected_seq += 1
            print(f"收到 Chunk {seq}")

        elif seq >= expected_seq:
            print(f"收到重複 Chunk {seq}，重新回傳 ACK")
            continue

        # 重複 Chunk 也需要回傳 ACK
        ack = struct.pack("!cI", b"A", seq)

        if DROP_ACK_ONCE and seq == 1 and not dropped:
            dropped = True
            print("模擬遺失 ACK 1")
            continue

        server.sendto(ack, client_addr)

    # 3. 等待 END
    while True:
        packet, addr = server.recvfrom(4096)

        if addr != client_addr:
            continue

        if packet == b"E":
            break

        # DATA ACK 遺失時，補回 ACK
        if len(packet) >= 5 and packet[:1] == b"D":
            seq = int.from_bytes(packet[1:5], "big")
            if seq < expected_seq:
                ack = struct.pack("!cI", b"A", seq)
                server.sendto(ack, client_addr)

    # 4. 重組並驗證
    content = b"".join(chunks[i] for i in range(count))
    actual_hash = hashlib.sha256(content).hexdigest()

    valid_file = (
        len(content) == size
        and actual_hash == expected_hash
    )

    if not valid_file:
        print("SHA-256 驗證失敗")
        result = b"X"
    else:
        save_path = SAVE_DIR / ("received_" + name)

        try:
            with open(save_path, "xb") as file:
                file.write(content)

            print("檔案儲存成功：", save_path)
            result = b"F"

        except FileExistsError:
            print("接收檔案已存在")
            result = b"X"

    server.sendto(result, client_addr)

    # 5. 短暫處理重複 END
    # 若 FINISH 遺失，Client 可能重傳 END
    deadline = time.monotonic() + 6

    while time.monotonic() < deadline:
        server.settimeout(
            max(0.01, deadline - time.monotonic())
        )

        try:
            packet, addr = server.recvfrom(4096)
        except socket.timeout:
            break

        if addr == client_addr and packet == b"E":
            server.sendto(result, client_addr)

print("Server 本次傳輸結束")
