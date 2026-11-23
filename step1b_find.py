import pdfplumber

targets = {
    "Balance Sheet": "TOTAL EQUITY AND LIABILITIES",
    "Profit & Loss": "Profit before tax",
    "Cash Flow": "Net cash from operating activities",
}

with pdfplumber.open("report.pdf") as pdf:
    for i, page in enumerate(pdf.pages, start=1):
        text = (page.extract_text() or "").lower()
        for name, phrase in targets.items():
            if phrase.lower() in text:
                print(f"Page {i}: {name}")