"""
NYC Citywide Payroll Portfolio Analysis (FY 2019-2025)
Generates figures saved to ../figures/
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings, os

warnings.filterwarnings('ignore')
sns.set_theme(style='whitegrid', palette='muted', font_scale=1.1)
plt.rcParams['figure.dpi'] = 120

# Resolve paths relative to this script's location
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES = os.path.join(ROOT, 'figures')
os.makedirs(FIGURES, exist_ok=True)

def fig_path(name):
    return os.path.join(FIGURES, name)

# ── 1. Load ────────────────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(ROOT, 'data', 'cleaned', 'payroll.csv'), low_memory=False)

df['Regular Hours'] = (
    df['Regular Hours']
    .astype(str).str.replace(',', '', regex=False)
    .pipe(pd.to_numeric, errors='coerce')
)

print(f"Rows: {len(df):,}  |  Agencies: {df['Agency Name'].nunique()}  |  Years: {sorted(df['Fiscal Year'].unique())}")

# ── 2. Salary normalisation ────────────────────────────────────────────────────
WORKING_DAYS = 260

def annualize(row):
    if row['Pay Basis'] == 'per Day':
        return row['Base Salary'] * WORKING_DAYS
    return row['Base Salary']

df['Annual Salary'] = df.apply(annualize, axis=1)
df['Total Compensation'] = df['Regular Gross Paid'] + df['Total OT Paid'] + df['Total Other Pay']

print("\nSalary by Pay Basis:")
print(df.groupby('Pay Basis')['Annual Salary'].agg(['count','mean','min','max']).round(0))

# ── 3. Payroll over time ───────────────────────────────────────────────────────
yearly = (
    df.groupby('Fiscal Year')
    .agg(
        Total_Payroll=('Total Compensation', 'sum'),
        Headcount=('First Name', 'count'),
        Avg_Compensation=('Total Compensation', 'mean')
    )
    .reset_index()
)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].bar(yearly['Fiscal Year'], yearly['Total_Payroll'] / 1e9, color=sns.color_palette('muted')[0])
axes[0].set_title('Total Payroll Spend (USD Billions)', fontweight='bold')
axes[0].set_xlabel('Fiscal Year')
axes[0].set_ylabel('$ Billions')
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}B'))
for _, row in yearly.iterrows():
    axes[0].text(row['Fiscal Year'], row['Total_Payroll']/1e9 + 0.05,
                 f"${row['Total_Payroll']/1e9:.1f}B", ha='center', fontsize=9)

axes[1].plot(yearly['Fiscal Year'], yearly['Avg_Compensation'], marker='o', linewidth=2.5,
             color=sns.color_palette('muted')[2])
axes[1].fill_between(yearly['Fiscal Year'], yearly['Avg_Compensation'], alpha=0.15,
                     color=sns.color_palette('muted')[2])
axes[1].set_title('Average Total Compensation per Employee', fontweight='bold')
axes[1].set_xlabel('Fiscal Year')
axes[1].set_ylabel('USD')
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

plt.tight_layout()
plt.savefig(fig_path('01_payroll_over_time.png'), bbox_inches='tight')
plt.close()

pct_growth = (yearly['Total_Payroll'].iloc[-1] / yearly['Total_Payroll'].iloc[0] - 1) * 100
print(f"\nPayroll growth FY2019 → FY2025: {pct_growth:.1f}%")

# ── 4. Agency breakdown ────────────────────────────────────────────────────────
agency_spend = (
    df.groupby('Agency Name')
    .agg(
        Total_Compensation=('Total Compensation', 'sum'),
        Headcount=('First Name', 'count'),
        Avg_Compensation=('Total Compensation', 'mean')
    )
    .sort_values('Total_Compensation', ascending=False)
    .reset_index()
)

top15 = agency_spend.head(15)

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(top15['Agency Name'].str.title(), top15['Total_Compensation'] / 1e9,
               color=sns.color_palette('muted', 15))
ax.invert_yaxis()
ax.set_title('Top 15 Agencies by Total Payroll Spend (FY 2019–2025)', fontweight='bold', pad=15)
ax.set_xlabel('Total Compensation ($ Billions)')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}B'))

for bar, val in zip(bars, top15['Total_Compensation']):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f'${val/1e9:.1f}B', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(fig_path('02_top_agencies.png'), bbox_inches='tight')
plt.close()

top3_share = top15.head(3)['Total_Compensation'].sum() / agency_spend['Total_Compensation'].sum() * 100
print(f"Top 3 agencies: {top3_share:.1f}% of all payroll")
print(top15[['Agency Name','Total_Compensation','Headcount']].head(5).to_string(index=False))

# ── 5. Overtime analysis ───────────────────────────────────────────────────────
ot_agency = (
    df[df['Total OT Paid'] > 0]
    .groupby('Agency Name')
    .agg(
        Total_OT=('Total OT Paid', 'sum'),
        Total_Gross=('Regular Gross Paid', 'sum'),
        OT_Workers=('First Name', 'count')
    )
    .assign(OT_Ratio=lambda x: x['Total_OT'] / x['Total_Gross'] * 100)
    .sort_values('Total_OT', ascending=False)
    .reset_index()
)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

top10_ot = ot_agency.head(10)
axes[0].barh(top10_ot['Agency Name'].str.title(), top10_ot['Total_OT'] / 1e9,
             color=sns.color_palette('flare', 10))
axes[0].invert_yaxis()
axes[0].set_title('Top 10 Agencies — Total OT Spend', fontweight='bold')
axes[0].set_xlabel('$ Billions')
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}B'))

top10_ratio = ot_agency[ot_agency['OT_Workers'] >= 500].nlargest(10, 'OT_Ratio')
axes[1].barh(top10_ratio['Agency Name'].str.title(), top10_ratio['OT_Ratio'],
             color=sns.color_palette('flare', 10))
axes[1].invert_yaxis()
axes[1].set_title('Top 10 Agencies — OT as % of Gross Pay', fontweight='bold')
axes[1].set_xlabel('Overtime / Regular Gross (%)')
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))

plt.tight_layout()
plt.savefig(fig_path('03_overtime_agencies.png'), bbox_inches='tight')
plt.close()

# OT trend
ot_trend = (
    df.groupby('Fiscal Year')
    .agg(Total_OT=('Total OT Paid', 'sum'), Total_Gross=('Regular Gross Paid', 'sum'))
    .assign(OT_Ratio=lambda x: x['Total_OT'] / x['Total_Gross'] * 100)
    .reset_index()
)

fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()
ax1.bar(ot_trend['Fiscal Year'], ot_trend['Total_OT'] / 1e9,
        color=sns.color_palette('flare')[2], alpha=0.8, label='OT Spend ($B)')
ax2.plot(ot_trend['Fiscal Year'], ot_trend['OT_Ratio'],
         color='#2d2d2d', marker='o', linewidth=2.5, label='OT Ratio (%)')
ax1.set_xlabel('Fiscal Year')
ax1.set_ylabel('OT Spend ($ Billions)', color=sns.color_palette('flare')[2])
ax2.set_ylabel('OT as % of Gross Pay')
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}B'))
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
ax1.set_title('Overtime Spend & Ratio by Fiscal Year', fontweight='bold')
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
plt.tight_layout()
plt.savefig(fig_path('04_overtime_trend.png'), bbox_inches='tight')
plt.close()

print("\nOT trend:")
print(ot_trend.to_string(index=False))

# ── 6. Top job titles ──────────────────────────────────────────────────────────
title_stats = (
    df.groupby('Title Description')
    .agg(
        Count=('First Name', 'count'),
        Avg_Salary=('Annual Salary', 'mean'),
        Avg_OT=('Total OT Paid', 'mean'),
        Avg_Total_Comp=('Total Compensation', 'mean')
    )
    .query('Count >= 200')
    .sort_values('Avg_Total_Comp', ascending=False)
    .reset_index()
)

top20 = title_stats.head(20)

fig, ax = plt.subplots(figsize=(13, 8))
ax.barh(top20['Title Description'].str.title(), top20['Avg_Salary'] / 1e3,
        label='Base Salary', color='#4c72b0')
ax.barh(top20['Title Description'].str.title(), top20['Avg_OT'] / 1e3,
        left=top20['Avg_Salary'] / 1e3, label='Overtime Pay', color='#dd8452')
ax.invert_yaxis()
ax.set_title('Top 20 Job Titles by Avg Total Compensation (min. 200 employees)', fontweight='bold')
ax.set_xlabel('Average Pay ($000s)')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}K'))
ax.legend()
plt.tight_layout()
plt.savefig(fig_path('05_top_titles.png'), bbox_inches='tight')
plt.close()

print("\nTop 10 titles by total comp:")
print(top20[['Title Description','Count','Avg_Salary','Avg_OT','Avg_Total_Comp']].head(10).round(0).to_string(index=False))

# ── 7. Tenure vs salary ────────────────────────────────────────────────────────
df['Agency Start Date'] = pd.to_datetime(df['Agency Start Date'], errors='coerce')
df['Ref Date'] = pd.to_datetime(df['Fiscal Year'].astype(str) + '-06-30')
df['Tenure Years'] = ((df['Ref Date'] - df['Agency Start Date']).dt.days / 365.25).round(0)
df_tenure = df[(df['Tenure Years'] >= 0) & (df['Tenure Years'] <= 45) & (df['Annual Salary'] < 400000)]

tenure_bins = pd.cut(df_tenure['Tenure Years'],
                     bins=[0, 2, 5, 10, 20, 30, 45],
                     labels=['<2y', '2-5y', '5-10y', '10-20y', '20-30y', '30y+'])
tenure_salary = df_tenure.groupby(tenure_bins, observed=True)['Annual Salary'].median()

fig, ax = plt.subplots(figsize=(10, 5))
tenure_salary.plot.bar(ax=ax, color=sns.color_palette('muted', len(tenure_salary)),
                       edgecolor='white', width=0.7)
ax.set_title('Median Annual Salary by Tenure Band', fontweight='bold')
ax.set_xlabel('Years at Agency')
ax.set_ylabel('Median Annual Salary')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
for bar in ax.patches:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
            f'${bar.get_height():,.0f}', ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(fig_path('07_tenure_salary.png'), bbox_inches='tight')
plt.close()

print("\nTenure vs median salary:")
print(tenure_salary)

# ── 8. Salary distribution by leave status ────────────────────────────────────
main_statuses = df['Leave Status as of June 30'].value_counts().head(3).index
df_status = df[df['Leave Status as of June 30'].isin(main_statuses) & (df['Annual Salary'] < 400000)]

fig, ax = plt.subplots(figsize=(11, 5))
for status, grp in df_status.groupby('Leave Status as of June 30'):
    grp['Annual Salary'].plot.kde(ax=ax, label=status, linewidth=2)
ax.set_title('Annual Salary Distribution by Leave Status', fontweight='bold')
ax.set_xlabel('Annual Salary (USD)')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.set_ylabel('Density')
ax.legend(title='Leave Status')
ax.set_xlim(0, 400000)
plt.tight_layout()
plt.savefig(fig_path('06_salary_by_status.png'), bbox_inches='tight')
plt.close()

print("\nAll figures saved to ../figures/")
print("Done.")
