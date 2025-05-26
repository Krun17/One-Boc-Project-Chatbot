import streamlit as st
from agents.query_understanding_agnet import extract_query_window_and_kpis
from agents.retrieval_agent import retrieve_chunks_for_query
from chatbot import final_response_agent
from dotenv import load_dotenv

load_dotenv()

# === Streamlit UI ===
st.set_page_config(page_title="🧠 Store Manager KPI Chatbot")
st.title("🧠 Store Manager KPI Chatbot")
st.markdown("Ask anything related to Net Sales, ABV, NOB, Complaints, etc.")

# === Store selection (optional if multi-store) ===
store_name = st.selectbox("Select Store:", ["GURUGRAM AMBI MALL"])

# === Query Input ===
user_query = st.text_area("Type your question:", placeholder="e.g. What is the Net Sales trend in last 7 days?")

# === Run Button ===
if st.button("Generate Insight") and user_query.strip():
    with st.spinner("Analyzing query and fetching insights..."):

        # === Step 1: Understand the query ===
        query_info = extract_query_window_and_kpis(user_query)

        # === Step 2: Retrieve relevant context chunks using days_back
        retrieved_chunks = retrieve_chunks_for_query(
            start_date=query_info['start_date'],
            end_date=query_info['end_date'],
            store_name=store_name,
            kpi_filters=query_info['mentioned_kpis'],
            user_query=user_query,
            top_k=query_info['days_back']  # ✅ This links everything together!
        )

        # === Step 3: Final Answer from LLM ===
        final_answer = final_response_agent(user_query, retrieved_chunks)

        st.markdown("### 📌 Answer:")
        st.markdown(final_answer)

        # Optional debug
        print("\n[DEBUG] Retrieved Chunks:\n", retrieved_chunks)

# === Footer ===
st.markdown("---")
st.markdown("Smart KPI Chatbot powered by LangChain")