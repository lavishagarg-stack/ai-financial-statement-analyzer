import json

with open("extracted.json") as f:
    data = json.load(f)
d = {i["name"]: i for i in data["items"]}

def cur(n): return d[n]["current_year"]
def prev(n): return d[n]["previous_year"]
def pg(n): return d[n]["page"]

def growth(n):
    return (cur(n) / prev(n) - 1) * 100

def ebitda(get):
    return get("profit_before_tax") + get("finance_costs") + get("depreciation_and_amortisation") - get("other_income")

print("ITC LIMITED - FINANCIAL ANALYSIS (Rs crore)\n")

print(f"Revenue growth: {growth('revenue_from_operations'):.1f}%  (Source: p. {pg('revenue_from_operations')})")
print(f"Net profit growth (reported): {growth('profit_for_the_year'):.1f}%  (Source: p. {pg('profit_for_the_year')})")
print(f"Profit growth, continuing operations: {growth('profit_from_continuing_operations'):.1f}%  (Source: p. {pg('profit_from_continuing_operations')})")
print("Note: last year's reported profit includes a one-off gain from discontinued operations.")
print(f"Net profit margin: {cur('profit_for_the_year') / cur('revenue_from_operations') * 100:.1f}%  (Source: p. {pg('profit_for_the_year')})")

e_cur, e_prev = ebitda(cur), ebitda(prev)
print(f"EBITDA: {e_cur:,.0f} vs {e_prev:,.0f} last year  (Source: p. {pg('profit_before_tax')})")
print(f"EBITDA margin: {e_cur / cur('revenue_from_operations') * 100:.1f}%")

print(f"Current ratio: {cur('current_assets') / cur('current_liabilities'):.2f}  (Source: p. {pg('current_assets')})")
print(f"Interest coverage: {(cur('profit_before_tax') + cur('finance_costs')) / cur('finance_costs'):.0f}x  (Source: p. {pg('finance_costs')})")

debt = (cur("non_current_borrowings") or 0) + (cur("current_borrowings") or 0)
print(f"Total borrowings: {debt:,.2f}  (Source: p. {pg('current_borrowings')})")
print(f"Debt to equity: {debt / cur('total_equity'):.2f}  (Source: p. {pg('total_equity')})")

print(f"Operating cash flow: {cur('net_cash_from_operating_activities'):,.0f}  (Source: p. {pg('net_cash_from_operating_activities')})")
