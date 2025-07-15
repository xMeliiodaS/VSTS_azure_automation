import pandas as pd


def work_with_exel():
    df = pd.read_excel("Escort - CARTOSOUND 4D - Clinical WF.xlsx")
    with_bugs = df[df["Bugs No. V8"].apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x))]

    for _, row in with_bugs.iterrows():
        id_and_defect = {}
        id_and_defect[f"ID: {row['ID']}"] = f"Bug: {round(row['Bugs No. V8'])}"
        print(id_and_defect)


work_with_exel()
