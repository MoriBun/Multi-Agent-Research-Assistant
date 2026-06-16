from google import genai
import chromadb
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()
client_llm = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
model = SentenceTransformer("all-MiniLM-L6-v2")

client_db = chromadb.PersistentClient(path="phase2/chroma_db")
collection = client_db.get_or_create_collection(name="nvidia_report")


def retrieve_chunks(question, n_results):
    question_embedding = model.encode(question)
    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=n_results
    )
    return results["documents"][0]


def build_prompt(question, chunks):
    context = "\n\n".join(chunks)
    return f"""Dựa vào thông tin sau từ báo cáo tài chính NVIDIA:

{context}

Hãy trả lời câu hỏi: {question}
Nếu thông tin không đủ để trả lời, hãy nói rõ là không tìm thấy thông tin liên quan."""


def ask_rag(question):
    chunks = retrieve_chunks(question, 3)
    prompt = build_prompt(question, chunks)

    response = client_llm.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


questions = [
    "What was NVIDIA's revenue growth in Q1 2027?",
    "What was NVIDIA's gross margin in Q1 2027?",
    "What is NVIDIA's stock symbol on a different exchange like Tokyo?"
]

for question in questions:
    print(f"Câu hỏi: {question}")
    answer = ask_rag(question)
    print(f"Chatbot: {answer}")
