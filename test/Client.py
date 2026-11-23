
import socket
import os

SERVER_IP = "127.0.0.1"
PORT = 5000
FILE_PATH = "test.txt"

file_size = os.path.getsize(FILE_PATH)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((SERVER_IP, PORT))

    # 傳送 8 bytes 的檔案大小
    client.sendall(file_size.to_bytes(8, "big"))

    with open(FILE_PATH, "rb") as file:
        while True:
            chunk = file.read(4096)

            if not chunk:
                break

            client.sendall(chunk)

    print("檔案已傳送")
    print("Server 回應：", client.recv(2).decode())
