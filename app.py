import os
import time
import json
import pdfplumber
import pandas as pd
import streamlit as st
from google import genai
from google.genai import types

MODELS = ["gemini-3.5-flash", "gemini-3-flash-preview", "gemini-2.5-flash"]

ITEMS = (
    "revenue_from_operations, other_income, total_income, finance_costs, "
    "depreciation_and_amortisation, profit_before_tax, profit_for_the_year, "
    "profit_from_continuing_operations, profit_from_discontinued_operations, "
    "total_equity, non_current_borrowings, current_borrowings, current_assets, "
    "current_liabilities, net_cash_from_operating_activities"
)

st.set_page_config(page_title="AI Financial Statement Analyzer", layout="wide")
st.title("AI Financial Statement Analyzer")
st.caption("Upload an annual report. Every number is linked to its source page.")

uploaded = st.file_uploader("Annual report PDF", type="pdf")
company = st.text_input("Company name", "ITC Limited")
col1, col2 = st.columns(2)
first = col1.number_input("First page of the financial statements", min_value=1, value=2)
last = col2.number_input("Last page of the financial statements", min_value=1, value=7)
st.caption("Open the PDF and check which pages hold the balance sheet, profit and loss, and cash flow statement.")


def read_pages(file, first, last):
    chunks = []
    with pdfplumber.open(file) as pdf:
        last = min(last, len(pdf.pages))
        for p in range(first, last + 1):
            text = pdf.pages[p - 1].extract_text() or ""
            chunks.append(f"=== PAGE {p} ===\n{text}")
    return "\n\n".join(chunks)


def extract(report_text, company):
    prompt = f"""
You are reading the financial statements of {company}.
Extract these items for the current year and the previous year, in the report's currency units.
For each item give the value and the page number where you found it.
Use null if an item is not on the pages. Use 0 if the report shows a dash.
Do NOT guess or calculate.

Items: {ITEMS}

Return JSON in this shape:
{{"items": [{{"name": "...", "current_year": 0, "previous_year": 0, "page": 0}}]}}

TEXT:
{report_text}
"""
    client = genai.Client()
    for round_no in range(3):
        for model_name in MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                data = json.loads(response.text)
                return {i["name"]: i for i in data["items"]}, model_name
            except Exception:
                continue
        time.sleep(20)
    return None, None


def compute(d):
    def cur(n):
        item = d.get(n)
        return item.get("current_year") if item else None

    def prev(n):
        item = d.get(n)
        return item.get("previous_year") if item else None

    def pg(n):
        item = d.get(n)
        return item.get("page") if item else None

    def growth(n):
        return (cur(n) / prev(n) - 1) * 100

    def ebitda():
        return (cur("profit_before_tax") + cur("finance_costs")
                + cur("depreciation_and_amortisation") - cur("other_income"))

    def debt():
        return (cur("non_current_borrowings") or 0) + (cur("current_borrowings") or 0)

    metrics = [
        ("Revenue growth", lambda: f"{growth('revenue_from_operations'):.1f}%", "revenue_from_operations"),
        ("Net profit growth (reported)", lambda: f"{growth('profit_for_the_year'):.1f}%", "profit_for_the_year"),
        ("Profit growth (continuing operations)", lambda: f"{growth('profit_from_continuing_operations'):.1f}%", "profit_from_continuing_operations"),
        ("Net profit margin", lambda: f"{cur('profit_for_the_year') / cur('revenue_from_operations') * 100:.1f}%", "profit_for_the_year"),
        ("EBITDA", lambda: f"{ebitda():,.0f}", "profit_before_tax"),
        ("EBITDA margin", lambda: f"{ebitda() / cur('revenue_from_operations') * 100:.1f}%", "profit_before_tax"),
        ("Current ratio", lambda: f"{cur('current_assets') / cur('current_liabilities'):.2f}", "current_assets"),
        ("Interest coverage", lambda: f"{(cur('profit_before_tax') + cur('finance_costs')) / cur('finance_costs'):.0f}x", "finance_costs"),
        ("Total borrowings", lambda: f"{debt():,.2f}", "current_borrowings"),
        ("Debt to equity", lambda: f"{debt() / cur('total_equity'):.2f}", "total_equity"),
        ("Operating cash flow", lambda: f"{cur('net_cash_from_operating_activities'):,.0f}", "net_cash_from_operating_activities"),
    ]

    rows = []
    for label, fn, key in metrics:
        try:
            value = fn()
            source = pg(key)
        except Exception:
            value, source = "not available", "-"
        rows.append({"Metric": label, "Value": value, "Source page": source})
    return rows


if st.button("Analyze", type="primary"):
    if uploaded is None:
        st.warning("Please upload a PDF first.")
    elif not os.environ.get("GEMINI_API_KEY"):
        st.error("GEMINI_API_KEY is not set on this computer.")
    else:
        with st.spinner("Reading the report and extracting numbers..."):
            text = read_pages(uploaded, int(first), int(last))
            d, model_used = extract(text, company)
        if d is None:
            st.error("Gemini is too busy right now. Try again in a few minutes.")
        else:
            st.success(f"Analysis complete (model: {model_used})")

            st.subheader("Analysis")
            st.dataframe(pd.DataFrame(compute(d)), hide_index=True, use_container_width=True)

            disc = d.get("profit_from_discontinued_operations", {}).get("previous_year")
            if disc:
                st.warning("Last year's reported profit includes a one-off result from discontinued operations. "
                           "Compare profit from continuing operations for a like-for-like view.")

            st.subheader("Extracted data and sources")
            raw = pd.DataFrame(list(d.values()))
            st.dataframe(raw, hide_index=True, use_container_width=True)
            st.caption("Always verify key figures against the original report.")