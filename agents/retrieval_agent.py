import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from datetime import datetime
import os

# === Load environment variables ===
load_dotenv()

# === Initialize ChromaDB client and collection ===
chroma_client = chromadb.PersistentClient(path="chroma_db")
embedding_function = embedding_functions.OpenAIEmbeddingFunction(model_name="text-embedding-ada-002")
collection = chroma_client.get_or_create_collection(
    name="store_kpi_chunks",
    embedding_function=embedding_function
)

# === Semantic Retrieval Function ===
def retrieve_chunks_for_query(start_date, end_date, store_name, user_query=None, days_back=7):
    # Step 1: Fetch 20 results from ChromaDB directly
    raw_results = collection.query(
        query_texts=[user_query],
        n_results=20,
        where={"store": store_name}
    )

    # Step 2: Post-filter by date and validate
    filtered_chunks = []
    for doc, meta in zip(raw_results.get("documents", [[]])[0], raw_results.get("metadatas", [[]])[0]):
        try:
            doc_date = datetime.strptime(meta["date"], "%Y-%m-%d").date()
            print(f"start_date: {start_date}, end_date: {end_date}, doc_date: {doc_date}")
            if start_date <= doc_date <= end_date:
                filtered_chunks.append(doc)
        except Exception as e:
            print(f"[⚠️] Skipping due to bad date format: {meta.get('date')} → {e}")

    print(f"[🔍] Retrieved {len(filtered_chunks)} chunks from ChromaDB (after date filtering).")
    return filtered_chunks

# === Optional Test Block ===
if __name__ == "__main__":
    from datetime import date

    chunks = retrieve_chunks_for_query(
        start_date=date(2025, 2, 21),
        end_date=date(2025, 2, 28),
        store_name="GURUGRAM AMBI MALL",
        user_query="What are the sales and sales trend in the last 7 days?"
    )

    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- Chunk {i} ---\n{chunk}")
