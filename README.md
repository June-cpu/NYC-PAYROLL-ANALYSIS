# NYC Citywide Payroll Analysis (FY 2019–2025)

Exploratory analysis of NYC Open Data's Citywide Payroll dataset — 500K+ employee records across 88 agencies and 7 fiscal years.

---

## Project Structure

```
nyc-payroll-analysis/
├── data/
│   ├── raw/payroll.csv          # Source data from NYC Open Data
│   └── cleaned/payroll.csv      # Cleaned output
├── notebooks/
│   └── nyc_payroll_portfolio.ipynb   # Full portfolio analysis
├── scripts/
│   ├── clean_data.py            # Data cleaning pipeline
│   └── portfolio_analysis.py    # Generates all figures
└── figures/                     # Chart outputs (generated)
```

---

## Key Questions

- Which agencies account for the highest payroll costs?
- How significant is overtime pay compared to base pay?
- Are certain job titles consistently high in overtime?
- How does total payroll change across fiscal years?
- Does tenure correlate with higher compensation?

---

## Methodology

**Data cleaning (`scripts/clean_data.py`)**
- Parsed numeric columns with comma/dollar-sign formatting
- Dropped ~70 rows (<0.001% of data) with negative Regular Gross Paid or OT Paid
- Parsed `Agency Start Date` as datetime

**Salary normalization**
- `per Annum` and `Prorated Annual` → used as-is
- `per Day` → multiplied by 260 working days to produce `Annual Salary`

**Total Compensation** = Regular Gross Paid + Total OT Paid + Total Other Pay

**Tenure** = calculated relative to fiscal year end (June 30) using `Agency Start Date`

---

## Key Findings

| # | Finding | Implication |
|---|---------|-------------|
| 1 | **Total payroll grew 454% from FY2019 to FY2025**, driven by DOE scaling headcount | Dept of Education now represents the dominant share of NYC workforce cost |
| 2 | **Top 3 agencies account for 83% of all payroll** — all three are DOE sub-agencies | Payroll reform is effectively an education workforce problem |
| 3 | **OT spiked in FY2024** (ratio doubled vs prior years) before normalizing in FY2025 | Likely a post-pandemic demand surge; worth monitoring for structural vs. temporary causes |
| 4 | **Principals average $191K total comp** — highest of any role with ≥200 employees | Leadership pipeline investment yields the highest per-person compensation returns |
| 5 | **Median salary peaks in the 20–30 year tenure band ($76K), then drops at 30+ years ($52K)** | Late-career drop likely reflects part-time or reduced-hour arrangements, not salary cuts |

---

## Analysis Sections

1. **Setup & Data Loading** — load, inspect, clean `Regular Hours` column
2. **Salary Normalization** — unify `per Day` / `per Annum` / `Prorated Annual` to a single `Annual Salary`
3. **Payroll Spending Over Time** — total bill and average compensation per employee by fiscal year
4. **Agency Cost Breakdown** — top 15 agencies by cumulative payroll spend
5. **Overtime Deep-Dive** — absolute OT spend and OT-to-gross ratio by agency; year-over-year OT trend
6. **Top Job Titles by Compensation** — stacked bar of base salary vs. OT for top 20 roles (≥200 employees)
7. **Salary Distribution by Leave Status** — KDE comparison across active, on-leave, and separated employees
8. **Tenure Analysis** — median salary across six tenure bands
9. **Key Findings** — summary table of insights with implications

---

## How to Run

```bash
# Set up environment
python -m venv .venv && source .venv/bin/activate
pip install pandas numpy matplotlib seaborn scipy jupyter

# Clean raw data
python scripts/clean_data.py

# Generate all figures
python scripts/portfolio_analysis.py

# Open notebook
jupyter notebook notebooks/nyc_payroll_portfolio.ipynb
```

---

## Data Source

[NYC Open Data — Citywide Payroll Data (Fiscal Year)](https://data.cityofnewyork.us/City-Government/Citywide-Payroll-Data-Fiscal-Year-/k397-673e)
