import traceback

class ExecAgent:
    def __init__(self, df, llm):
        """
        df : precomputed pandas DataFrame
        llm : any LLM that can take a prompt and return a string (OpenAI, Groq, etc.)
        """
        self.df = df
        self.llm = llm

    def run(self, query: str) -> str:
        try:
            # 🔧 Step 1: Ask LLM to write Python code using pandas
            code_prompt = f"""
You are a pandas expert. Write Python code to answer this question based on a precomputed DataFrame called `df`.

Question: {query}

⚠️ Only write code. Assign the final result to a variable called `result`.
"""
            code = self.llm(code_prompt)

            # 🧪 Step 2: Run the generated code in a safe exec scope
            local_vars = {"df": self.df.copy()}
            exec(code, {}, local_vars)

            result = local_vars.get("result", None)
            if result is None:
                return "⚠️ Code ran but no result was returned."

            # 🧠 Step 3: Use LLM to structure the output as a nice answer
            final_summary_prompt = f"""
Below is the raw result from pandas after running a query:

{result}

Please convert this into a clear and helpful explanation for a store manager.
"""
            answer = self.llm(final_summary_prompt)
            return answer.strip()

        except Exception as e:
            return f"❌ Error running generated code:\n{traceback.format_exc()}"
