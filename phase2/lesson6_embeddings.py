import fitz
from sentence_transformers import SentenceTransformer
import chromadb


def load_pdf(file_path):
    doc = fitz.open(file_path)
    pages = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        pages.append(page.get_text())

    print(f"Tổng số trang: {doc.page_count}")
    doc.close()
    return pages


def split_into_chunks(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        # Move forward by (chunk_size - overlap) so the next chunk
        # re-uses the last 'overlap' words of the current chunk.
        # This prevents losing information at chunk boundaries.
        start += chunk_size - overlap

    return chunks


pages = load_pdf("phase2/data/NVIDIA Announces Financial Results for First Quarter Fiscal 2027.pdf")

# Join all pages into one string before chunking,
# because split_into_chunks works on a single text, not a list
full_text = " ".join(pages)
print(f"Tổng số từ: {len(full_text.split())}")

chunks = split_into_chunks(full_text)
print(f"Số chunks: {len(chunks)}")

# Load the embedding model (downloaded once, cached locally afterward)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Embed all chunks at once — faster than encoding one by one
embeddings = model.encode(chunks)
print(f"Shape của embeddings: {embeddings.shape}")

# PersistentClient stores vectors on disk so data survives between runs
client = chromadb.PersistentClient(path="phase2/chroma_db")
collection = client.get_or_create_collection(name="nvidia_report")

collection.add(
    documents=chunks,
    embeddings=embeddings.tolist(),  # ChromaDB needs plain lists, not numpy arrays
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)

questions = [
    "What was the revenue in Q1 2027?",
    "How did the data center business perform?"
]

for question in questions:
    question_embedding = model.encode(question)

    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=2
    )

    print(f"\nCâu hỏi: {question}")
    print("Chunks liên quan nhất:")
    for doc in results["documents"][0]:
        print(f" - {doc}")
