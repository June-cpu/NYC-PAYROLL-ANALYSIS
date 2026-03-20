Data Set: Citywide Payroll Data by Fiscal year

Analyze payroll spending across NYC agencies to identify
trends, high-cost departments, and overtime patterns.

Key Questions:
- Which agencies account for the highest payroll costs?
- How significant is overtime pay compared to base pay?
- Are certain job titles consistently high in overtime?
- How does total payroll change across fiscal years?

---------------------------------------------------------------------------

Problems:

- Negative values given when looking at an overview of the data // Solved
		- sicne there were only around 70 collective negaitve values in the wrong places, I just dropped them because they are only about 0.0008% of the entire dataset

- Some of the payroll information comes in pay per day and others come in pay per year // Solved
	- Base Salary before normalization:
count  501421.000000
mean    57221.231797
std     48495.804483
min        20.450000
25%        33.180000
50%     61407.000000
75%     97469.000000
max    336563.000000
	- the min of $20.45 and 25th percentile of $33.18 are clearly daily rates not annual, they come from the 166,127 rows where Pay Basis = "per Day"
	- Solution: multiply "per Day" salaries by 260 working days to get Annual Salary, leave "per Annum" and "Prorated Annual" as-is
	- after normalization the per Day mean goes from ~$15K to ~$391K which is in line with the rest of the dataset

- Regular Hours column stored as strings with comma formatting (e.g. "1,820") // Solved
	- this caused the column to be read as object dtype instead of numeric
	- Solution: strip commas before converting to numeric with pd.to_numeric()

- Dataset only contains Manhattan as the Work Location Borough // Known limitation
	- all 501,421 rows have Work Location Borough = "MANHATTAN"
	- borough-level comparison is not possible with this slice of the data
	- likely a filter applied when the data was exported, not a data quality issue

- Pay Basis has three categories, two of which behave the same way // Noted
	- "per Annum" (334,268 rows) and "Prorated Annual" (1,026 rows) are both annual figures
	- "per Day" (166,127 rows) needed conversion
	- "Prorated Annual" rows are a very small slice (~0.2%) so treated the same as per Annum