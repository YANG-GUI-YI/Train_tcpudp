import socket

Host = "0.0.0.0"
Port = 5000

def recv_exact(conn,size):
    data = bytearray()
    while len(data) < size:
        chunk = conn.recv(min(4096, size - len(data)))

        if not chunk:
            raise ConnectionError("連線中斷")
        
        data.extend(chunk)

    return bytes(data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((Host, Port))
    server.listen(1)
    
    print("等待連線中...")

    conn, addr = server.accept()
    with conn:
        
        print(f"已連線: {addr}")

        file_size= int.from_bytes(recv_exact(conn, 8), byteorder='big')

        received=0

        with open("received_file", "wb") as file:
            while received < file_size:
                chunk = conn.recv(min(4096, file_size - received))
                if not chunk:
                    raise ConnectionError("連線中斷")
                file.write(chunk)
                received += len(chunk)
        conn.sendall(b"OK")
        print("檔案接收完成")