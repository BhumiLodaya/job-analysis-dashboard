import pandas as pd

df=pd.read_csv("C:/Users/bhumi/OneDrive/Desktop/professional/internship/job/Salaries.csv")
print(df.info)
print(df.columns)
print(df.isnull().sum)
df=df.drop_duplicates()

df.to_csv("C:/Users/bhumi/OneDrive/Desktop/professional/internship/job/Salaries_cleaned.csv")
