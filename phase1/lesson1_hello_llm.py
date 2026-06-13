"""
Bài 1 — Hello LLM
Mục tiêu: Gửi message đầu tiên tới Gemini và hiểu cấu trúc request/response.
"""

import os
from dotenv import load_dotenv
from google import genai

# Bước 1: Load API key từ file .env
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Không tìm thấy GOOGLE_API_KEY trong file .env!")

# Bước 2: Khởi tạo client với API key
client = genai.Client(api_key=api_key)

# Bước 3: Gửi message và nhận response
print("Đang gửi message tới Gemini...")
print("-" * 50)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Xin chào! Hãy giải thích 'token' trong LLM là gì, bằng tiếng Việt, trong 3 câu ngắn."
)

# Bước 4: In kết quả
print("Câu trả lời từ Gemini:")
print(response.text)

print("-" * 50)
print("Hoàn thành! Bạn vừa gọi LLM API lần đầu tiên.")
