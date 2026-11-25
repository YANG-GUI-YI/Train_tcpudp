
import socket
from pathlib import Path

HOST = "140.125.111.95"
PORT = 5000
BUFFER_SIZE = 4096

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "test.txt"

# 取得檔案大小
file_size = FILE_PATH.stat().st_size

FILE_NAME = FILE_PATH.name
NAME_DATA = FILE_NAME.encode("utf-8")
name_size = len(NAME_DATA)

if name_size > 255:
    raise ValueError("檔案名稱過長，無法傳送")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))

    client.sendall(name_size.to_bytes(2, "big"))
    client.sendall(NAME_DATA)

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
