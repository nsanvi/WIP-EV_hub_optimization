import pandas as pd
import json

with open('2023_2T_Punts_Recarrega_Vehicle_Electric.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df.to_csv("puntos_recarga_barcelona.csv", index=False, encoding='utf-8-sig')

print("Convertido a CSV exitosamente")