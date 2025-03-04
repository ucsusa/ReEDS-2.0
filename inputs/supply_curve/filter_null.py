# Remove null spur lengths from supply curve files.
import pandas as pd
import os
from glob import glob
from pathlib import Path

if __name__ == "__main__":

    curr_dir = Path(os.path.dirname(os.path.realpath(__file__)))

    files = glob(str(curr_dir/'*.csv'))

    for file in files:
        fname = file.split('/')[-1]
        if 'supply_curve' not in fname:
            continue
        elif any(value in fname for value in ['egs','geohydro', 'geo', 'csp']):
            continue
        elif not any(value in fname for value in ['ba','county']):
            continue
        else:
            df = pd.read_csv(file)
            try:
                n_nulls = df['dist_spur_km'].isnull().sum().sum()
                if n_nulls > 0:
                    print(f"editing file: {file}")
                    df_nulls = df.loc[df['dist_spur_km'].isnull()].copy()
                    df_nonulls = df.loc[~df['dist_spur_km'].isnull()].copy()
                    # get mean for region and class
                    df_nonulls_grouped = df_nonulls.groupby(['region','class']).mean()

                    for row in df_nulls.itertuples():
                        try:
                            df.at[row.Index, 'trans_adder_per_mw'] = df_nonulls_grouped.loc[(row.region, row._2), 'trans_adder_per_mw']
                            df.at[row.Index, 'dist_spur_km'] = df_nonulls_grouped.loc[(row.region, row._2), 'dist_spur_km']
                        except KeyError as e:
                            # forward fill
                            df.at[row.Index, 'trans_adder_per_mw'] = df.at[row.Index-1, 'trans_adder_per_mw']
                            df.at[row.Index, 'dist_spur_km'] = df.at[row.Index-1, 'dist_spur_km']

                    df['supply_curve_cost_per_mw'] = df['trans_adder_per_mw'] + df['capital_adder_per_mw']
                    print(n_nulls, df['dist_spur_km'].isnull().sum())
                    df.to_csv(file)
                else:
                    pass
            except KeyError as e:
                print(f"Key Error in {file}")
                raise e