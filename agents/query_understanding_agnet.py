import re
import string
from datetime import datetime, timedelta

# === KPI Synonym Map ===
kpi_synonym_map = {
    "net sales": "daily_sales",  # ✅ Mapped to precomputed daily
    "sales": "daily_sales",
    "abv": "average_bill_value",
    "average bill value": "average_bill_value",
    "nob": "number_of_bills",
    "number of bills": "number_of_bills",
    "basket builder": "basket_builder_availability",
    "basket builder availability": "basket_builder_availability",
    "availability": "availability",
    "promotion": "promotion_cost",
    "ad spend": "promotion_cost",
    "advertisement cost": "promotion_cost",
    "customer complaints": "complaints_resolved_offline",
    "offline complaints": "complaints_resolved_offline",
    "sla": "jiomart_sla_adherence",
    "jiomart sla": "jiomart_sla_adherence"
}


# === KPI Detection Function ===
def detect_mentioned_kpis(query: str, kpi_synonym_map: dict) -> list:
    mentioned = set()
    query_clean = query.translate(str.maketrans('', '', string.punctuation)).lower()
    for keyword, standard_kpi in kpi_synonym_map.items():
        if keyword in query_clean:
            mentioned.add(standard_kpi)
    return list(mentioned) if mentioned else ["Net Sales"]

# === Query Understanding Agent ===
def extract_query_window_and_kpis(query: str):
    query_clean = query.translate(str.maketrans('', '', string.punctuation)).lower()

    # Hardcoded today for offline testing/debugging
    today = datetime.strptime("2025-02-28", "%Y-%m-%d").date()
    print(f"[🧠 DEBUG] 'Today' is set to: {today}")

    # === Date Range Logic ===
    if "yesterday" in query_clean:
        start_date = end_date = today - timedelta(days=1)
    elif "today" in query_clean:
        start_date = end_date = today
    elif match := re.search(r"last (\d+) days", query_clean):
        days = int(match.group(1))
        start_date = today - timedelta(days=days - 1)
        end_date = today
    elif "this week" in query_clean:
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif "last week" in query_clean:
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = start_date + timedelta(days=6)
    elif "last month" in query_clean:
        last_month_end = today.replace(day=1) - timedelta(days=1)
        start_date = last_month_end.replace(day=1)
        end_date = last_month_end
    else:
        # Default fallback: full current month till today
        start_date = today.replace(day=1)
        end_date = today

    mentioned_kpis = detect_mentioned_kpis(query, kpi_synonym_map)
    days_back = (end_date - start_date).days + 1

    print(f"[🧠 DEBUG] Extracted Range: {start_date} to {end_date} ({days_back} days)")
    print(f"[🧠 DEBUG] Detected KPIs: {mentioned_kpis}")

    return {
        "start_date": start_date,
        "end_date": end_date,
        "days_back": days_back,
        "mentioned_kpis": mentioned_kpis
    }

# === Example Test ===
if __name__ == "__main__":
    sample_query = "What is the Net Sales and ABV trend for the last 7 days?"
    result = extract_query_window_and_kpis(sample_query)
    print(result)
