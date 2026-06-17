import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import yfinance as yf
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
db_client = chromadb.PersistentClient(path="phase2/chroma_db")
collection = db_client.get_or_create_collection(name="nvidia_report")

# Tool 1: real stock price
def get_stock_price(symbol):
    ticker = yf.Ticker(symbol)
    return ticker.info.get("currentPrice", "Không tìm thấy giá")

# Tool 2: RAG on financial report
def query_financial_report(question):
    question_embedding = embed_model.encode(question)
    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=3
    )
    chunks = results["documents"][0]
    context = "\n\n".join(chunks)

    prompt = f"""Dựa vào thông tin sau từ báo cáo tài chính NVIDIA:

{context}

Hãy trả lời câu hỏi: {question}
Nếu thông tin không đủ để trả lời, hãy nói rõ là không tìm thấy thông tin liên quan.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# Declare 2 tools for LLM

tools = types.Tool(function_declarations=[
    {
        "name": "get_stock_price",
        "description": "Lấy giá cổ phiếu hiện tại theo mã cổ phiếu",
        "parameters": {
            "type": "object",
            "properties": {"symbol": {"type":"string", "description": "Mã cổ phiếu như AAPL, NVDA"}},
            "required": ["symbol"]
        }
    },
    {
        "name": "query_financial_report",
        "description": "Tìm câu trả lời trong báo cáo tài chính NVIDIA dựa trên câu hỏi",
        "parameters": {
            "type": "object",
            "properties": {"question": {"type":"string", "description": "Câu hỏi về nội dung báo cáo"}},
            "required": ["question"]
        }
    }
])

# Map function name to real function and call follow LLM name return
available_functions = {
    "get_stock_price": get_stock_price,
    "query_financial_report": query_financial_report
}

config = types.GenerateContentConfig(
    system_instruction="Bạn là trợ lý phân tích cổ phiếu NVIDIA. Dùng get_stock_price cho câu hỏi về giá cổ phiếu hiện tại và dùng query_financial_report cho câu hỏi về nội dung báo cáo tài chính",
    tools=[tools]
)

history = []

while True:
    user_input = input("Bạn: ")
    if user_input.lower() == "exit":
        break

    history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=history,
        config=config
    )

    part = response.candidates[0].content.parts[0]

    if part.function_call:
        func_name = part.function_call.name
        func_args = dict(part.function_call.args)

        # Call real function base on LLM name required
        result = available_functions[func_name](**func_args)

        function_response_content = types.Content(
            role="user",
            parts=[types.Part.from_function_response(name=func_name, response={"result": result})]
        )

        response2 = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents= history + [response.candidates[0].content, function_response_content],
            config=config
        )

        print("Chatbot:", response2.text)
        history.append(response.candidates[0].content)
        history.append(function_response_content)
        history.append(response2.candidates[0].content)
    else:
        history.append(response.candidates[0].content)
        print("Chatbot:", part.text)
