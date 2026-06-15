import fitz

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

# Print the first 3 words of each of the first 3 chunks to verify
# that overlap is working — consecutive chunks should share some words
for i, chunk in enumerate(chunks[:3]):
    first_3_words = chunk.split()[:3]
    print(f"Chunk {i + 1} bắt đầu bằng: {first_3_words}")