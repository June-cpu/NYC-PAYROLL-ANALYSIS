import numpy as np
import pandas as pd


def clean_data(data):
    
	data["Fiscal Year"] = pd.to_numeric(data["Fiscal Year"], errors="coerce")

	pay_cols = [
        "Base Salary",
        "Regular Gross Paid",
        "OT Hours",
        "Total OT Paid",
        "Total Other Pay"
    ]

	for col in pay_cols:
		data[col] = (data[col].astype(str).str.replace(",", "", regex = False).str.replace("$", "", regex = False))
		data[col] = pd.to_numeric(data[col], errors="coerce")


	data["Agency Start Date"] = pd.to_datetime(data["Agency Start Date"], errors="coerce")
	#drop rows with negative values from regular pay and overtime
	data = data[
		(data["Regular Gross Paid"] >= 0) &
		(data["Total OT Paid"] >= 0)
	]

	return data



def main():
	data = pd.read_csv("data/raw/payroll.csv", low_memory=False)
	data = clean_data(data)
	data.to_csv("data/cleaned/payroll.csv", index=False)
	
	print(data["Base Salary"].head(10))

	print( "---------------------------------------------------------")

	print(data[[
    "Base Salary",
    "Regular Gross Paid",
    "OT Hours",
    "Total OT Paid",
    "Total Other Pay"
	]].describe())

	print( "---------------------------------------------------------")

	print((data["Regular Gross Paid"] < 0).sum() )
	print((data["Total OT Paid"] < 0).sum() )




if __name__ == "__main__":
	main()
