
import socket

HOST = "127.0.0.1"
PORT = 5000

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
        header = recv_exact(conn, 8)
        file_size = int.from_bytes(header, "big")

        print("預期接收：", file_size, "bytes")
        data = recv_exact(conn, file_size)
        print("實際接收：", len(data), "bytes")
        conn.sendall(b"ok")
print("傳輸完成，Server 已斷線")
