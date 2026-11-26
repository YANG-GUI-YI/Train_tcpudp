
import socket

SERVER_IP = "192.168.56.1"
SERVER_PORT = 5001

BUFFER_SIZE = 4096

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:

    client.settimeout(3)

    while True:
        message = input("輸入訊息：")

        client.sendto(
            message.encode("utf-8"),
            (SERVER_IP, SERVER_PORT)
        )

        if message == "/exit":
            break

        try:
            data, addr = client.recvfrom(BUFFER_SIZE)

            print("Server 回應：", data.decode("utf-8"))

        except socket.timeout:
            print("等待回應逾時：可能發生封包遺失或 Server 沒有回應")

print("UDP Client 已結束")
