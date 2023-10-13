import requests
import json

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import time

# get the data

headers = {
    'authority': 'bahn.expert',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,de;q=0.7',
    'referer': 'https://bahn.expert/details/S%2038318/2023-10-11T05:24:00.000Z?administration=801539',
}

date = []
departure = []
arrival = []

#                               ⬇️ skip 9 and 10 because they are error prone
for i in [1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]:
    params = {
        'initialDepartureDate': '2023-09-'+str(i).zfill(2)+'T05:56:00.000Z',
        'administration': '801539',
    }

    response = requests.get('https://bahn.expert/api/journeys/v1/details/S%2038318', params=params, headers=headers)
    print(params['initialDepartureDate'] + ": " + str(response))

    date.append(params["initialDepartureDate"])
    # explainer:     ⬇️ read jsonfrom api     ⬇️ 9th stop is WiesWdf   ⬇️ real ⬇️ only the hour timestamp
    departuretime = json.loads(response.content)["stops"][11]["departure"]["time"][11:16]
    arrivaltime = json.loads(response.content)["stops"][14]["arrival"]["time"][11:16]

    departuretimeh = int(departuretime[:2]) + int(departuretime[3:])/60
    arrivaltimeh = int(arrivaltime[:2]) + int(arrivaltime[3:])/60

    departure.append(departuretimeh)
    arrival.append(arrivaltimeh)

# plot the data

df_data = {'Category': date, 'Upper': departure, 'Lower': arrival}
df = pd.DataFrame(data=df_data)
df['Height'] = df['Upper'] - df['Lower']

ax = df.plot(kind='bar', y='Height', x='Category', bottom=df['Lower'],
             color='darkgreen', legend=False)
ax.axhline(0, color='black')
ax.set_ylim(6, 7) #sets the y range

ax.hlines(y=[6+(1/60),6+(12/60)], xmin=[0,0], xmax=[len(arrival),len(arrival)]) # hline for wdf departure and ma-arena arrival

plt.tight_layout()
plt.show()
