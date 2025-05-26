import pandas as pd
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os

load_dotenv()

def create_chunks_from_excel(file_path, store_name, persist_path="chroma_db"):
    # Read Excel
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()  # Clean column names
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    # No store filtering needed

    # Group by Date
    chunks = []
    metadatas = []
    for date, group in df.groupby("Date"):
        lines = [f"Store: {store_name}", f"Date: {date}"]
        for col in group.columns:
            if col != "Date":
                val = group[col].values[0]
                lines.append(f"{col}: {val}")
        chunks.append("\n".join(lines))
        metadatas.append({"store": store_name, "date": date})

    # Embed and store in Chroma
    client = PersistentClient(path=persist_path)
    embedding_fn = embedding_functions.OpenAIEmbeddingFunction(model_name="text-embedding-ada-002")
    collection = client.get_or_create_collection("store_kpi_chunks", embedding_function=embedding_fn)

    ids = [f"{store_name}_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)
    print(f"[✅] Stored {len(chunks)} chunks for {store_name}.")

if __name__ == "__main__":
    create_chunks_from_excel("Data/Ambi mall Data - Precomputed.xlsx", "GURUGRAM AMBI MALL")
