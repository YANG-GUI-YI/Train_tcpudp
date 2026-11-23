
import socket

HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 4096
received_size = 0

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

        with open("received.bin", "wb") as file:

            while received_size < file_size:

                remaining = file_size - received_size

                data = conn.recv(min(BUFFER_SIZE, remaining))

                if not data:
                    raise ConnectionError("檔案尚未傳輸完成，連線已中斷")

                file.write(data)

                received_size += len(data)

                print(f"接收進度：{received_size}/{file_size}")

        print("檔案接收完成！")

print("傳輸完成，Server 已斷線")

