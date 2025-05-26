from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from rag.Chunk_Creator import create_chunks_from_excel
from dotenv import load_dotenv
import os

# === Load API key ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found. Please check your .env file.")

# === Vector Store Builder ===
def build_vectorstore(excel_path, store_name, persist_dir="chroma_db"):
    # ✅ Read chunk text + metadata from Excel
    chunk_texts, metadatas = [], []
    create_chunks_from_excel(excel_path, store_name, persist_path=persist_dir)

    print(f"[✅] Chroma Vector Store created for: {store_name} at {persist_dir}")

# === Entry Point ===
if __name__ == "__main__":
    print("[⚙️] Building Chroma Vector Store from Excel...")
    build_vectorstore("Data/Ambi mall Data - Precomputed.xlsx", "GURUGRAM AMBI MALL")
    print("[✅] Chroma vector store persisted successfully.")
