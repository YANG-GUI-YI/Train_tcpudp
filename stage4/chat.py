
import socket
import threading

MAX_MESSAGE = 65536


def recv_exact(conn, size):
    data = bytearray()

    while len(data) < size:
        chunk = conn.recv(size - len(data))

        if not chunk:
            return None

        data.extend(chunk)

    return bytes(data)


def receive_messages(conn, stop_event):
    try:
        while not stop_event.is_set():

            header = recv_exact(conn, 4)

            if header is None:
                print("\n對方已關閉傳送方向")
                break

            size = int.from_bytes(header, "big")

            if size > MAX_MESSAGE:
                raise ValueError("訊息長度超過限制")

            data = recv_exact(conn, size)

            if data is None:
                print("\n接收不完整，連線已中斷")
                break

            message = data.decode("utf-8")

            if message == "/exit":
                print("\n對方要求結束聊天")
                print("請輸入 /exit 完成關閉")
                continue

            print(f"\n對方：{message}")

    except (OSError, ValueError, UnicodeError) as e:
        print("\n接收發生錯誤：", e)

    finally:
        stop_event.set()


def start_chat(conn):
    stop_event = threading.Event()

    receive_thread = threading.Thread(
        target=receive_messages,
        args=(conn, stop_event)
    )
    receive_thread.start()

    print("聊天開始，輸入 /exit 結束")

    try:
        while True:
            message = input("我：")

            data = message.encode("utf-8")

            if len(data) > MAX_MESSAGE:
                print("訊息過長")
                continue

            conn.sendall(len(data).to_bytes(4, "big"))
            conn.sendall(data)

            if message == "/exit":
                print("已送出結束通知")
                break

    except (OSError, EOFError, KeyboardInterrupt) as e:
        print("\n停止傳送：", e)

    finally:
        try:
            # 只關閉傳送方向
            conn.shutdown(socket.SHUT_WR)
        except OSError:
            pass

        # 等待接收 Thread 結束
        receive_thread.join()

        print("聊天已結束")
