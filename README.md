\# AI Financial Statement Analyzer



Reads a company's annual report (PDF) and produces a structured financial analysis,

with every number linked to its source page.



\## What it does

\- Extracts key figures from the financial statements (revenue, profit, borrowings, working capital, operating cash flow)

\- Calculates growth, margin, liquidity and leverage ratios in plain Python (the maths is not done by the AI)

\- Cites the report page for each figure

\- Flags one-off items, such as profit distorted by discontinued operations



\## How it works

1\. pdfplumber reads the selected pages and labels each with its page number

2\. Gemini API returns the figures as structured JSON, with the page for each

3\. Python and pandas calculate the ratios

4\. Streamlit shows the results



\## Validation

Tested on ITC Limited's FY2026 consolidated financial statements.

27 of 27 extracted data points matched figures read manually from the report.

Tested on one company and one report so far, so results on other report formats may differ.



\## Run it

```

pip install -r requirements.txt

```

Set your own Gemini API key as an environment variable named GEMINI\_API\_KEY, then:

```

python -m streamlit run app.py

```



\## Files

\- app.py: the Streamlit app

\- extract.py, ratios.py: command-line version of the extraction and ratio steps

\- validate.py: compares extracted numbers with manually checked ones

\- step1b\_find.py: finds the pages that hold the financial statements



\## Limitations

\- You choose the page range of the financial statements

\- Tested only on ITC so far

\- Always verify key figures against the original report

