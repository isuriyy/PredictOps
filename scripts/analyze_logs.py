import pandas as pd

df = pd.read_csv("data/synthetic/pipeline_logs.csv")

print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nFailure Count:")
print(df["failed"].value_counts())

print("\nSLA Breaches:")
print(df["sla_breach"].value_counts())
