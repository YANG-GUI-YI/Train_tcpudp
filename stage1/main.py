import os
from pathlib import Path


# 取得 main.py 所在的資料夾
BASE_DIR = Path(__file__).resolve().parent

# 組合檔案路徑
source_path = BASE_DIR / "test.txt"
received_path = BASE_DIR / "received.txt"
BUFFER_SIZE = 4096  
with open(source_path, "rb") as source:
    count = 0
    while True:
        count += 1
        data = source.read(BUFFER_SIZE)
        print(f"第 {count} 次讀取：{len(data)} Bytes")

        if not data:
            print("已到達 EOF，結束讀取")
            break


print("目前工作目錄：", os.getcwd())
print("程式所在位置：", Path(__file__).resolve().parent)