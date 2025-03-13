import pandas as pd
from website.DatabaseConnector import DatabaseConnector
# Load the Excel file
file_path = '../Pre-season Rosters.xlsx'
xls = pd.ExcelFile(file_path)

# List all sheet names
sheet_names = xls.sheet_names

def process_sheet(sheet_name):
    if sheet_name not in ["Receiving3", "Rushing3", "Receiving2", "Rushing2", "Receiving", "Rushing", "Passing"]:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df['Team'] = sheet_name  # Add a column for the team name (sheet name)
        print(f"Processed sheet: {sheet_name}")
        return df
    else:
        print(f"Skipped sheet: {sheet_name}")
        return None
# Process the sheets
dfs = [process_sheet(sheet) for sheet in sheet_names]

# Filter out None values
dfs = [df for df in dfs if df is not None]
# # Concatenate all DataFrames
all_data = pd.concat(dfs, ignore_index=True)

# Separate by position
qbs = all_data[all_data['Pos.'] == 'QB']
rb_te_wr = all_data[all_data['Pos.'].isin(['RB', 'TE', 'WR'])]
db = DatabaseConnector()

# qbs_columns = [
#     '#', 'Player', 'Pos.', 'School', 'Orig. Team', 'NFL Exp.', 'Gms', 'Att',
#     'Cmp', 'Pct', 'Yds', 'YPA', 'TD', 'TD%', 'Int', 'YPG', 'Sack', 'RAtt',
#     'RYds', 'RAvg', 'RYPG', 'RLg', 'RTD', 'Team'
# ]

rb_te_wr_columns = [
    '#', 'Player', 'Pos.', 'School', 'Orig. Team', 'NFL Exp.', 'Gms', 'RAtt',
    'RYds', 'RAvg', 'RYPG', 'RLg', 'RTD', 'Rec', 'ReYds', 'ReAvg', 'ReYPG',
    'ReLg', 'ReTD', 'Tar', 'Team'
]
# Insert QB data
# for _, row in qbs[qbs_columns].iterrows():
#     params = tuple(row)
#     print(params)
#     db.insert(
#         """
#         INSERT INTO qb_data (number, player, pos, school, orig_team, nfl_exp, gms, att, cmp, pct, yds, ypa, td, td_pct, inter, ypg, sack, ratt, ryds, ravg, rypg, rlg, rtd, team)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """,
#         params
#     )

# # Insert RB, TE, WR data
for _, row in rb_te_wr[rb_te_wr_columns].iterrows():
    params = tuple(row)
    db.insert(
        """
        INSERT INTO rb_wr_te_data (number, player, pos, school, orig_team, nfl_exp, gms, ratt, ryds, ravg, rypg, rlg, rtd, rec, reyds, reavg, reypg, relg, retd, tar, team)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        params
    )

db.close()
print("Done")