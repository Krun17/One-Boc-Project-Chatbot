import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from datetime import datetime
import os

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
    # Step 1: Fetch a buffer of 50 results from ChromaDB
    raw_results = collection.query(
        query_texts=[user_query],
        n_results=20,  # buffer — we will trim later
        where={"store": store_name}
    )

    # Step 2: Post-filter by date and validate
    filtered_chunks = []
    for doc, meta in zip(raw_results.get("documents", [[]])[0], raw_results.get("metadatas", [[]])[0]):
        try:
            doc_date = datetime.strptime(meta["date"], "%Y-%m-%d").date()
            if start_date <= doc_date <= end_date:
                filtered_chunks.append((doc_date, doc))  # keep date for sorting
        except Exception as e:
            print(f"[⚠️] Skipping due to bad date format: {meta.get('date')} → {e}")

    # Step 3: Sort by date and keep first 20 only
    filtered_chunks.sort(key=lambda x: x[0])  # sort ascending by date
    final_chunks = [doc for _, doc in filtered_chunks[:20]]  # max 20 for LLM

    print(f"[🔍] Retrieved {len(final_chunks)} chunks from ChromaDB (after filtering & sorting).")
    return final_chunks

# === Optional Test Block ===
if __name__ == "__main__":
    from datetime import date
    chunks = retrieve_chunks_for_query(
        start_date=date(2025, 2, 21),
        end_date=date(2025, 2, 28),
        store_name="GURUGRAM AMBI MALL",
        user_query="What are the sales and sales trend in the last 7 days?"
    )
    for chunk in chunks:
        print("\n---\n", chunk)
