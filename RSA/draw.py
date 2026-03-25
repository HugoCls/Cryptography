import pandas as pd

def filter_valid_lines(file_path, num_colons):
    valid_lines = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            if line.count(':') == num_colons:
                valid_lines.append(line.strip())
    return valid_lines

def create_dataframe_from_lines(lines, column_names, sep='::'):
    data = [line.split(sep) for line in lines]
    df = pd.DataFrame(data, columns=column_names)
    return df

# Filtrer les lignes valides pour le fichier d'encryption
valid_lines_encrypt = filter_valid_lines('alice_results.txt', 6)
df_encrypt = create_dataframe_from_lines(valid_lines_encrypt, 
                                         ['plaintext', 'ciphertext', 'key_creation_time', 'encryption_time'])

# Filtrer les lignes valides pour le fichier de décryption
valid_lines_decrypt = filter_valid_lines('bob_results.txt', 4)
df_decrypt = create_dataframe_from_lines(valid_lines_decrypt, 
                                         ['ciphertext', 'deciphered_text', 'decryption_time'])

# Afficher les DataFrames
print("Encryption Data:")
print(df_encrypt.head())
print("\nDecryption Data:")
print(df_decrypt.head())

# Récupérer des statistiques sur key_creation_time
df_encrypt['key_creation_time'] = pd.to_numeric(df_encrypt['key_creation_time'], errors='coerce')
key_creation_stats = df_encrypt['key_creation_time'].describe()
print("\nStatistics for key_creation_time:")
print(key_creation_stats)
