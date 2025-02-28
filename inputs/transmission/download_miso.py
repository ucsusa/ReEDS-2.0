import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import osmnx as ox
from us import states
import camelot
import time
from tqdm import tqdm
from pathlib import Path

if __name__ == "__main__":

    states_of_interest = [
                        #   'North Dakota',
                        #   'South Dakota',
                        # 'Minnesota',
                        # 'Illinois',
                        # 'Wisconsin',
                        # 'Missouri',
                        # 'Indiana',
                        # 'Michigan',
                        # 'Kentucky',
                        'Iowa'
                        ]


    save_path = Path("spatial-data/osmnx_download/").resolve()
    save_path.mkdir(parents=True, exist_ok=True)

    # get counties in each state -- this will yield more data than necessary
    # frames = []
    for state in states_of_interest:
        print(state)
        state_abbr = states.lookup(state).abbr.lower()
        tables = pd.read_html(f'https://en.wikipedia.org/wiki/List_of_counties_in_{state.replace(" ", "_")}')
        # this is super hacky and not guaranteed to always work
        try:
            county_list = tables[1]['County'].to_list()
        except: 
            county_list = tables[0]['County'].to_list()

        start = time.perf_counter()
        pbar = tqdm(county_list, position=0, leave=True)
        for county in pbar:
            # disambiguation
            if county == "Saint Louis City":
                county = "Saint Louis"
            pbar.set_description(f"Processing {county}")
            county_name = f"{county}, {state}, United States"
            county_inf = ox.features_from_place(county_name, tags={"power":True})
            county_inf['COUNTY'] = county
            # frames.append(county_inf)
            save_name = county.lower().replace(' county', '')
            save_to = save_path / f"{state_abbr}_{save_name}_infrastructure.csv"
            county_inf.to_csv(str(save_to))
        end = time.perf_counter()
        print(f"Total download took {end-start:.3f} seconds")