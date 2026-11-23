import json
import pdfplumber
from google import genai
from google.genai import types

MODEL = "gemini-3.5-flash"
PAGES = [2, 3, 4, 5, 6, 7]

# 1. Read the chosen pages and label each with its page number
chunks = []
with pdfplumber.open("report.pdf") as pdf:
    for p in PAGES:
        text = pdf.pages[p - 1].extract_text() or ""
        chunks.append(f"=== PAGE {p} ===\n{text}")
report_text = "\n\n".join(chunks)

# 2. Ask Gemini for structured numbers
prompt = f"""
You are reading the consolidated financial statements of ITC Limited.
Extract these items for the current year and the previous year, in Rs crore.
For each item give the value and the page number where you found it.
Use null if an item is not on the pages. Do NOT guess or calculate.

Items: revenue_from_operations, other_income, total_income, finance_costs,
depreciation_and_amortisation, profit_before_tax, profit_for_the_year,
total_equity, non_current_borrowings, current_borrowings , current_assets, current_liabilities,net_cash_from_operating_activities, profit_from_continuing_operations,
profit_from_discontinued_operations.


Return JSON in this shape:
{{"items": [{{"name": "...", "current_year": 0, "previous_year": 0, "page": 0}}]}}

TEXT:
{report_text}
"""

import time

MODELS = ["gemini-3.5-flash", "gemini-3-flash-preview", "gemini-2.5-flash"]

client = genai.Client()
response = None
for round_no in range(4):
    for model_name in MODELS:
        try:
            print(f"Trying {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            break
        except Exception as e:
            print("  failed:", str(e)[:80])
    if response is not None:
        break
    print("All models busy, waiting 30 seconds...")
    time.sleep(30)

if response is None:
    raise SystemExit("Gemini is too busy right now. Try again in a while.")
data = json.loads(response.text)
with open("extracted.json", "w") as f:
    json.dump(data, f, indent=2)

for item in data["items"]:
    print(item)