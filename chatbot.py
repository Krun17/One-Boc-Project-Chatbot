from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
from agents.exec_agent import ExecAgent  # ✅ Fallback agent import
import pandas as pd

# === Load .env file ===
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# === Initialize LLM ===
llm = ChatOpenAI(model='gpt-4', temperature=0.2, openai_api_key=openai_api_key)

# === Prompt Template ===
prompt_template = ChatPromptTemplate.from_template("""
You are a retail KPI assistant. Below is the precomputed or raw KPI data for the selected store and date range:

{context}

The user has asked the following question:

{query}

Based on the provided data, respond with clear, concise, and actionable business-friendly insights.
Do not assume any KPI values. Only use what's given in the context.
""")

def final_response_agent(query: str, retrieved_chunks: list, fallback_df: pd.DataFrame = None) -> str:
    """
    Takes user query and relevant retrieved chunks,
    builds a structured prompt, and returns LLM response.
    Falls back to ExecAgent if no chunks retrieved.
    """
    if not retrieved_chunks:
        print("⚠️ No relevant chunks found. Using ExecAgent fallback.")
        if fallback_df is None:
            return "❌ No data available to answer the query."
        exec_agent = ExecAgent(df=fallback_df, llm=llm)
        return exec_agent.run(query)

    context = "\n\n".join(retrieved_chunks)

    # 🔍 Debug: Print what will go to the LLM
    print("\n[🧠 DEBUG] Prompt Context Sent to LLM:\n", context)
    print("\n[🗣️ DEBUG] Query Sent to LLM:\n", query)

    # Format prompt and get LLM response
    messages = prompt_template.format(query=query, context=context)
    response = llm(messages)

    return response.content

# === CLI Test ===
if __name__ == "__main__":
    sample_query = "What is the Net Sales trend over the last 7 days?"
    sample_chunks = []  # Simulating no chunks retrieved

    # Load precomputed fallback DataFrame
    fallback_df = pd.read_excel("Data/Ambi mall Data - Precomputed.xlsx")

    result = final_response_agent(sample_query, sample_chunks, fallback_df)
    print("\n[📌 FINAL ANSWER]\n", result)