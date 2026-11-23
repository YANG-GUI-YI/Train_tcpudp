import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
def calculate_sha256(file_path):
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sha.update(data)
    return sha.hexdigest()

source_file = BASE_DIR / "position_zero.png"
received_file = BASE_DIR / "received.png"

source_hash = calculate_sha256(source_file)
received_hash = calculate_sha256(received_file)
print(f"Source file SHA-256: {source_hash}")
print(f"Received file SHA-256: {received_hash}")
if source_hash == received_hash:
    print("檔案驗證成功，兩個檔案內容一致")
else:
    print("檔案驗證失敗，兩個檔案內容不一致")