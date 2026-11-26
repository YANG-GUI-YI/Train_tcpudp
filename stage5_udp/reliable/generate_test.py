
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FILE_PATH = BASE_DIR / "test.txt"

# 建立 10 KiB 的測試資料
data = b"ABCDEFGHIJ" * 1024

with open(FILE_PATH, "wb") as file:
    file.write(data)

print("測試檔案建立完成")
print("檔案大小：", FILE_PATH.stat().st_size, "Bytes")
