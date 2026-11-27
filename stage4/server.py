import socket
from chat import start_chat

HOST = "192.168.56.1"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(1)

    print("Server 等待 Client 連線...")

    conn, addr = server.accept()

    with conn:
        print("已連線：", addr)
        start_chat(conn)

print("Server 已關閉")