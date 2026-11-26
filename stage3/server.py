import socket
from pathlib import Path

HOST = "192.168.56.1"
PORT = 5000
BUFFER_SIZE = 4096
MAX_FILE_SIZE = 100 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
SAVE_DIR = BASE_DIR / "received_files"
SAVE_DIR.mkdir(exist_ok=True)
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
        name_size = int.from_bytes(recv_exact(conn, 2), "big")
        if not 1 <= name_size <= 255:
            print(f"檔案名稱長度 {name_size} 不合法，必須介於 1 到 255")
        NAME_DATA = recv_exact(conn, name_size)
        FILE_NAME = NAME_DATA.decode("utf-8")
        if (
            FILE_NAME in (".", "..")
            or "/" in FILE_NAME
            or "\\" in FILE_NAME
            or ":" in FILE_NAME
            or "\x00" in FILE_NAME
            or any(ord(c) < 32 for c in FILE_NAME)
            or FILE_NAME.endswith((".", " "))
        ):
            raise ValueError("檔名不合法")

        
        header = recv_exact(conn, 8)
        file_size = int.from_bytes(header, "big")

        if file_size > MAX_FILE_SIZE:
            print(f"檔案大小 {file_size} 超過限制 {MAX_FILE_SIZE}")
        print("接收檔名：", FILE_NAME)
        print("檔案大小：", file_size)

        save_path = SAVE_DIR / FILE_NAME
        
        received_size = 0
        print("目前工作目錄：", Path.cwd())
        print("預計儲存位置：", SAVE_DIR / FILE_NAME)
        print("來源設定是否為 PNG：", (SAVE_DIR / FILE_NAME).suffix == ".png")
        with open(SAVE_DIR / FILE_NAME, "xb") as file:
            while received_size < file_size:
                remaining = file_size - received_size
                data = conn.recv(min(BUFFER_SIZE, remaining))

                if not data:
                    raise ConnectionError("檔案尚未傳輸完成，連線已中斷")

                file.write(data)
                received_size += len(data)

                print(f"接收進度：{received_size}/{file_size}")

        print("檔案接收完成！")
        print("檔案是否存在：", (SAVE_DIR / FILE_NAME).exists())

        if (SAVE_DIR / FILE_NAME).exists():
            print("實際檔案大小：", (SAVE_DIR / FILE_NAME).stat().st_size)
        conn.sendall(b"OK")