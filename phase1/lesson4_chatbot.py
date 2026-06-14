import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import yfinance as yf

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# This function fetches the real current stock price from Yahoo Finance
def get_stock_price(symbol):
    ticker_obj = yf.Ticker(symbol)
    info = ticker_obj.info
    return info.get("currentPrice", "Không tìm thấy giá cổ phiếu")

# This tells the LLM what tools it can request, and what each tool does
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

# history stores every turn of the conversation so the LLM remembers context
history = []

# config is shared across all LLM calls to keep behavior and tools consistent
config = types.GenerateContentConfig(
    system_instruction="Bạn là trợ lý phân tích cổ phiếu. Bạn có thể trả lời câu hỏi chung về công ty, thị trường chứng khoán bằng kiến thức của bạn. Khi cần giá cổ phiếu thực tế, hãy dùng tool get_stock_price.",
    tools=[get_stock_price_tool]
)

while True:
    user_input = input("Bạn: ")
    if user_input.lower() == "exit":
        break

    # Add the user message to history before sending
    history.append(types.Content(
        role="user",
        parts=[types.Part(text=user_input)]
    ))

    # Send the full conversation history so the LLM has context
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=history,
        config=config
    )

    part = response.candidates[0].content.parts[0]

    if part.function_call:
        # The LLM decided it needs real data and is requesting a tool call
        func_name = part.function_call.name
        func_args = dict(part.function_call.args)

        # We run the actual Python function ourselves and get the real result
        result = get_stock_price(func_args["symbol"])

        # Package the function result as a Content object to send back to the LLM
        function_response_content = types.Content(
            role="user",
            parts=[types.Part.from_function_response(
                name=func_name,
                response={"symbol": func_args["symbol"], "price": result}
            )]
        )

        # Send history plus the tool exchange so the LLM can give a final answer
        response2 = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history + [response.candidates[0].content, function_response_content],
            config=config
        )

        print("Chatbot:", response2.text)

        # Save the full tool exchange into history for future context
        history.append(response.candidates[0].content)   # model requested a tool
        history.append(function_response_content)         # we returned the result
        history.append(response2.candidates[0].content)  # model gave the final answer

    else:
        # The LLM answered directly without needing any tool
        history.append(response.candidates[0].content)
        print("Chatbot:", part.text)




