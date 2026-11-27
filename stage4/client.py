import socket
from chat import start_chat

HOST = "192.168.56.1"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))

    print("成功連線至 Server")

    start_chat(client)

print("Client 已關閉")