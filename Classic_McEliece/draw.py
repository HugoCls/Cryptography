import pandas as pd

df = pd.read_csv('mceliece_-key_-creation_results.txt', names=['key_creation_time'])

# Get statistics on key_creation_time
df['key_creation_time'] = pd.to_numeric(df['key_creation_time'], errors='coerce')

key_creation_stats = df['key_creation_time'].describe()
print("\nStatistics for key_creation_time:")
print(key_creation_stats)
