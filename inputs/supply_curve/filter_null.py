# Remove null spur lengths from supply curve files.
import pandas as pd
import os
from glob import glob
from pathlib import Path

if __name__ == "__main__":

    curr_dir = Path(os.path.dirname(os.path.realpath(__file__)))

    files = glob(str(curr_dir/'*.csv'))

    for file in files:
        if 'supply_curve' not in file.split('/')[-1]:
            continue
        else:
            df = pd.read_csv(file)
            try:
                df = df.dropna(subset='dist_spur_km', how='any', axis=0)
                df.to_csv(file)
            except:
                continue