
import socket
from pathlib import Path

HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 4096

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "position_zero.png"

# 取得檔案大小
file_size = FILE_PATH.stat().st_size

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))

    # 傳送 8 Bytes 的檔案大小
    header = file_size.to_bytes(8, "big")
    client.sendall(header)

    sent_size = 0

    with open(FILE_PATH, "rb") as file:
        while True:
            data = file.read(BUFFER_SIZE)

            if not data:
                break

            client.sendall(data)
            sent_size += len(data)

            print(f"已傳送：{sent_size}/{file_size} Bytes")

    # 等待 Server 回覆
    response = client.recv(2)

    if response == b"OK":
        print("Server 已確認接收完成")
    else:
        print("沒有收到有效的完成確認")
