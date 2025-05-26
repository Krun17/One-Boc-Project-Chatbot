# ✅ Updated Retrieval Agent to match new chunk structure
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

# === Initialize Chroma Client ===
chroma_client = chromadb.PersistentClient(path="chroma_db")
embedding_function = embedding_functions.OpenAIEmbeddingFunction(model_name="text-embedding-ada-002")
collection = chroma_client.get_or_create_collection(name="store_kpi_chunks", embedding_function=embedding_function)

# ✅ Updated Retrieval Agent to match new chunk structure
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

# === Initialize Chroma Client ===
chroma_client = chromadb.PersistentClient(path="chroma_db")
embedding_function = embedding_functions.OpenAIEmbeddingFunction(model_name="text-embedding-ada-002")
collection = chroma_client.get_or_create_collection(name="store_kpi_chunks", embedding_function=embedding_function)

# === Semantic Retrieval Agent ===
def retrieve_chunks_for_query(start_date, end_date, store_name, user_query=None):
    # Step 1: Query ChromaDB for relevant semantic chunks by store
    raw_results = collection.query(
        query_texts=[user_query],
        n_results=20,  # high limit, filter later
        where={"store": store_name}
    )

    # Step 2: Post-filter by date range
    final_docs = []
    for doc, meta in zip(raw_results.get("documents", [[]])[0], raw_results.get("metadatas", [[]])[0]):
        doc_date = datetime.strptime(meta["date"], "%Y-%m-%d").date()
        if start_date <= doc_date <= end_date:
            final_docs.append(doc)

    print(f"[🔍] Retrieved {len(final_docs)} chunks after filtering from ChromaDB.")
    return final_docs

# === Example Test ===
if __name__ == "__main__":
    from datetime import date
    chunks = retrieve_chunks_for_query(
        start_date=date(2025, 2, 21),
        end_date=date(2025, 2, 28),
        store_name="GURUGRAM AMBI MALL",
        user_query="What are the trends in Net Sales and Availability over the last 7 days?"
    )
    for chunk in chunks:
        print("\n---\n", chunk)


# === Example Test ===
if __name__ == "__main__":
    from datetime import date
    chunks = retrieve_chunks_for_query(
        start_date=date(2025, 2, 21),
        end_date=date(2025, 2, 28),
        store_name="GURUGRAM AMBI MALL",
        user_query="What are the trends in Net Sales and Availability over the last 7 days?"
    )
    for chunk in chunks:
        print("\n---\n", chunk)
