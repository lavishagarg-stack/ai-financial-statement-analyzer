import json

with open("extracted.json") as f:
    data = json.load(f)
tool = {i["name"]: i for i in data["items"]}

# Type the numbers YOU read from report.pdf: (current year, previous year)
# Leave None for anything you have not checked yet.
manual = {
    "revenue_from_operations": (89913.33, 81612.78),               # page 3
    "other_income": (2425.80, 2529.69),                          # page 3
    "finance_costs": (85.17, 45.06),                         # page 3
    "depreciation_and_amortisation": (1710.53, 1646.32),   # page 3
    "profit_before_tax": (28033.39, 26926.94),             # page 3
    "profit_from_continuing_operations": (21018.15, 20036.47),  # page 3
    "profit_from_discontinued_operations": (None, 15016.01),    # page 3
    "profit_for_the_year": (21018.15, 35052.48),           # page 3
    "total_equity": (72873.02, 70397.94),                  # page 2                      
     "current_assets": (50708.41, 43893.28),                # page 2
    "current_liabilities": (16687.27, 14334.11),           # page 2
    "net_cash_from_operating_activities": (18464.31, 17627.04),  # page 6
     "non_current_borrowings": (60.00, 0),                  # page 2
    "current_borrowings": (2126.22, 91.26),                # page 2
}

checked = 0
correct = 0
for name, (m_cur, m_prev) in manual.items():
    for label, m_val, key in (("current", m_cur, "current_year"), ("previous", m_prev, "previous_year")):
        if m_val is None:
            continue
        checked += 1
        t_val = tool[name][key]
        ok = t_val is not None and abs(t_val - m_val) < 0.01
        if ok:
            correct += 1
        print(f"{'MATCH' if ok else 'MISMATCH'}  {name} ({label}): tool={t_val}  manual={m_val}")

print(f"\nChecked {checked} data points, {correct} matched.")
if checked:
    print(f"Accuracy: {correct / checked * 100:.1f}%")