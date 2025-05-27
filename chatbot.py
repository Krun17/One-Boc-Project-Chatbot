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
You are a smart retail KPI assistant. Below is the precomputed daily KPI data for the selected store and date range:

{context}

The user has asked the following question:

{query}

🧠 Instructions:
- If the user asks for **Sales**, use the `daily_sales` column.
- If the user asks for **Sales Trend** or **how sales are moving**, use the precomputed `slope_daily_sales` value:
  - A positive slope indicates an upward trend 📈
  - A negative slope indicates a downward trend 📉
  - A slope close to 0 indicates no significant trend ➖
- If the user asks **why a KPI dropped or increased**, analyze related metrics (e.g., ABV, NOB, Availability, Complaints, Promotions) for that date and previous date.
- Only refer to `net_sales` if the user says "MTD", "monthly", or mentions "total sales".
- Use KPIs like `sales_picked_up`, `sales_dropped`, `is_highest_sales_day`, `abv_x_nob`, etc. to infer reasons.
- If data for a specific date is missing, say so.
- Keep answers:
  - 🎯 Specific to the question
  - 📊 Data-backed
  - 🧾 Business-friendly and concise
""")


# === Final Response Agent ===
def final_response_agent(query: str, retrieved_chunks: list, fallback_df: pd.DataFrame = None) -> str:
    if not retrieved_chunks:
        print("⚠️ No relevant chunks found. Using ExecAgent fallback.")
        if fallback_df is None:
            return "❌ No data available to answer the query."
        exec_agent = ExecAgent(df=fallback_df, llm=llm)
        return exec_agent.run(query)

    # 🧩 Combine Chunks
    context = "\n\n".join(retrieved_chunks)

    # 🔍 Debug: Print retrieved chunks clearly
    print("\n====== 🔍 Retrieved Chunks Passed to LLM ======")
    for i, chunk in enumerate(retrieved_chunks, 1):
        print(f"\n--- Chunk {i} ---\n{chunk}")
    print("==============================================\n")

    # 🔧 Format prompt using LangChain's ChatPromptTemplate
    prompt_value = prompt_template.format_prompt(query=query, context=context)

    # 🧠 Debug print: print messages in structured format
    print("\n====== 🧠 Structured Prompt Messages ======")
    for msg in prompt_value.to_messages():
        print(f"{msg.type.upper()}: {msg.content}")
    print("==========================================\n")

    # ✅ Send to LLM
    response = llm.invoke(prompt_value.to_messages())
    return response.content



# === CLI Test ===
if __name__ == "__main__":
    sample_query = "What is the Net Sales trend over the last 7 days?"
    sample_chunks = []  # Simulating no chunks retrieved

    # Load precomputed fallback DataFrame
    fallback_df = pd.read_excel("Data/Ambi mall Data - Precomputed.xlsx")

    result = final_response_agent(sample_query, sample_chunks, fallback_df)
    print("\n[📌 FINAL ANSWER]\n", result)
