#!/usr/bin/env python

'''
This script loads the XLS file from argument and aggregates the data. It also
extracts the last day of data into its own dataset. The output is saved both
in CSV and JSON format under the `output` folder.
'''

import os
import sys
import pandas as pd
from pathlib import Path
import tempfile
import wget

# Root path of the project
ROOT = Path(os.path.dirname(__file__)) / '..'

# Download provided URL locally
fname = tempfile.NamedTemporaryFile().name
wget.download(sys.argv[1], fname)

# Read XLS file from disk
df = pd.read_excel(fname).sort_values(['DateRep', 'GeoId'])

# Compute the cumsum of values
columns = ['DateRep', 'GeoId', 'CountryExp', 'Confirmed', 'Deaths']
df_ = pd.DataFrame(columns=columns)
for country in df['GeoId'].unique():
    subset = df[df['GeoId'] == country].copy()
    subset['Confirmed'] = subset['NewConfCases'].cumsum()
    subset['Deaths'] = subset['NewDeaths'].cumsum()
    df_ = pd.concat([df_, subset[columns]])

df_ = df_[columns]
df_.columns = ['Date', 'CountryCode', 'CountryName', 'Confirmed', 'Deaths']
df = df_

# Extract a subset with only the latest date
df_latest = pd.DataFrame(columns=list(df.columns))
for country in df['CountryCode'].unique():
    df_latest = pd.concat([df_latest, df[df['CountryCode'] == country].iloc[-1:]])

# Save dataset in CSV format into output folder
df.to_csv(ROOT / 'output' / 'aggregated.csv', index=False)
df_latest.to_csv(ROOT / 'output' / 'latest.csv', index=False)
df_latest.to_csv('latest.csv', index=False)

# Save dataset in JSON format into output folder
df.to_json(ROOT / 'output' / 'aggregated.json', orient='records')
df_latest.to_json(ROOT / 'output' / 'latest.json', orient='records')