
import socket

HOST = "127.0.0.1"
PORT = 5000
file_data = b"A" * 2000
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))
    header = len(file_data).to_bytes(8, "big")
    client.sendall(header)
    client.sendall(file_data)

    response = client.recv(2)
    print("Server 回應：", response.decode("utf-8"))