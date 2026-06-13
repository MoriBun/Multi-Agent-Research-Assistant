# Import
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Hàm python lấy giá cổ phiếu (giả)
def get_stock_price(symbol):
    stock_prices = {
        "AAPL": 150.25,
        "GOOGL": 2800.50,
        "AMZN": 3400.75
    }
    return stock_prices.get(symbol, "Không tìm thấy mã cổ phiếu")

# định nghĩa tool cho LLM
get_stock_price_tool = types.Tool(function_declarations=[{
        "name": "get_stock_price",
        "description": "Lấy giá cổ phiếu hiện tại theo mã cổ phiếu.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Mã cổ phiếu như AAPL, TSLA"
                }
            },
            "required": ["symbol"]
        }
}])

# gửi câu hỏi kèm tool
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Giá cổ phiếu AAPL hôm nay là bao nhiêu?",
    config=types.GenerateContentConfig(tools=[get_stock_price_tool])
)

# Kiểm tra LLM có muốn gọi tool không
part = response.candidates[0].content.parts[0]

if part.function_call:
    func_name = part.function_call.name
    func_args = dict(part.function_call.args)
    print(f"LLM muốn gọi hàm: {func_name} với args: {func_args}")

    # tự chạy hàm thật
    result = get_stock_price(func_args["symbol"])
    print(f"Kết quả từ hàm: {result}")

    # gửi kết quả hàm về cho LLM
    response2 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part(text="Giá cổ phiếu AAPL hôm nay là bao nhiêu?"),
            types.Part(function_call=part.function_call),
            types.Part.from_function_response(name=func_name, response={"symbol": func_args["symbol"], "price": result})
        ]
    )
    print("\n Câu trả lời cuối:", response2.text)
else:
    print("LLM không muốn gọi tool, câu trả lời:", part.text)


