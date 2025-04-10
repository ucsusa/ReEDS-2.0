import pandas as pd
import numpy as np
from glob import glob
import os
from pathlib import Path
import us

if __name__ == "__main__":

    curr_dir = Path(os.path.dirname(os.path.realpath(__file__)))

    scenarios = ["current policy", "central high data center", "central"]

    path = Path(f"C:/Users/SDotson/OneDrive - Union of Concerned Scientists/Documents/2025/reeds-project-data/2025.02.10_UCS_shape_outputs/shape_outputs/")


    output_name = {'current policy':'EER_Current_UCS_load_hourly.h5',
                   'central high data center':'EER_HighDC_UCS_load_hourly.h5',
                   'central':'EER_Central_UCS_load_hourly.h5'}

    county_to_ba = pd.read_csv(str(curr_dir/"../../inputs/county2zone.csv"))
    load_participation = pd.read_csv(str(curr_dir/"../inputs/load/load_participation_factors_st_to_ba.csv"))

    name_to_abbr = {state.name.lower():state.abbr for state in us.STATES_CONTINENTAL}

    frames = []
    for scenario in scenarios:
        # get all files for a given scenario
        files = glob(str(path/scenario)+'/*.csv')
        for f in files:
            if 'summary_shapes' in f:
                continue
            else:
                # get the year
                year = int(f.split('\\')[-1].strip('.csv'))
                print(f'Processing {scenario} - {year}', flush=True, end = '\r')
                date_range = pd.date_range(start=f'{year}-01-01', 
                                        end=f'{year+1}-01-01', 
                                        freq='h', 
                                        inclusive='left')[:8760]
                df = pd.read_csv(f, parse_dates=True)
                df['year'] = year
                df = df.groupby(['weather_datetime', 'year']).sum().loc[:, 'alabama':]
                df['scenario'] = scenario
                df['weather_year'] = 2012
                df = df.reset_index()
                df = df[:8760]
                df.rename(columns={'weather_datetime':'datetime'}, inplace=True)
                df['datetime'] = date_range
                frames.append(df)
        print('\n')
    combined = pd.concat(frames, axis=0).set_index('datetime')

    # ReEDS BAs include D.C. as part of Maryland
    combined['maryland'] = combined['district of columbia'] + combined['maryland']
    combined = combined.drop(columns=['district of columbia'])
    combined = combined.rename(columns=name_to_abbr)

    print("Disaggregating data...")
    # disaggregate states into ReEDS BAs and scale by load factor
    combined_disagg = pd.DataFrame({int(row.ba.strip('p')):(combined[row.state].values\
                                                            *load_participation.loc[load_participation['ba']==row.ba,'factor'].values[0]) 
                                    for row in county_to_ba.itertuples()})
    
    # add important metadata
    combined_disagg['scenarios'] = combined['scenario'].reset_index(drop=True)
    combined_disagg['year'] = combined['year'].reset_index(drop=True)
    combined_disagg['index'] = np.tile(np.arange(0,8760),6*3)
    combined_disagg = combined_disagg.set_index(['scenarios','year','index'])

    # reformat the data to match other datasets from EER in ReEDS. Specifically,
    # indices appear to be (hour, ba) with years as the data variables (i.e.,
    # columns).
    print("Formatting data...")
    combined_formatted = combined_disagg.reset_index()\
                                        .melt(id_vars=['scenarios',
                                                       'year',
                                                       'index'], 
                                              value_vars=list(range(1,135)))\
                                        .pivot_table(values='value',
                                                     index=['scenarios',
                                                            'index',
                                                            'variable'],
                                                     columns=['year'])
    
    combined_formatted.columns = [str(y) for y in range(2025, 2055, 5)]

    combined_xarr = combined_formatted.to_xarray()

    print("Saving data...")
    for scenario in scenarios:
        xds = combined_xarr.sel(scenarios=scenario)
        xds.to_netcdf(str(curr_dir/f"../../inputs/load/{output_name[scenario]}"))
    print('Done!')