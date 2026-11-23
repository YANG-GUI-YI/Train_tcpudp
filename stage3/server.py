import socket
from pathlib import Path

HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 4096
MAX_FILE_SIZE = 100 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
SAVE_PATH = BASE_DIR / "received.png"

def recv_exact(conn, size):
    data = bytearray()
    while len(data) < size:
        packet = conn.recv(size - len(data))
        if not packet:
            raise ConnectionError("資料未完整接收，Client 已斷線")
        data.extend(packet)
    return bytes(data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(1)

    print("Server 正在等待連線...")

    conn, addr = server.accept()

    with conn:
        print("Client 已連線：", addr)
        conn.settimeout(30)
        header = recv_exact(conn, 8)
        file_size = int.from_bytes(header, "big")

        if file_size > MAX_FILE_SIZE:
            print(f"檔案大小 {file_size} 超過限制 {MAX_FILE_SIZE}")
            conn.sendall(b"NO")
            conn.close()
            exit()

        received_size = 0
        print("目前工作目錄：", Path.cwd())
        print("預計儲存位置：", SAVE_PATH)
        print("來源設定是否為 PNG：", SAVE_PATH.suffix == ".png")
        with open(SAVE_PATH, "wb") as file:

            while received_size < file_size:
                remaining = file_size - received_size
                data = conn.recv(min(BUFFER_SIZE, remaining))

                if not data:
                    raise ConnectionError("檔案尚未傳輸完成，連線已中斷")

                file.write(data)
                received_size += len(data)

                print(f"接收進度：{received_size}/{file_size}")

        print("檔案接收完成！")
        print("檔案是否存在：", SAVE_PATH.exists())

        if SAVE_PATH.exists():
            print("實際檔案大小：", SAVE_PATH.stat().st_size)
        conn.sendall(b"OK")