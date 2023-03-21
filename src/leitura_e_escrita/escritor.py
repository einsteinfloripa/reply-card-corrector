from pathlib import Path  
import pandas as pd

def escrever_csv(df, path):
    filepath = Path(path)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index = False )