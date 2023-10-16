#! /bin/python3

import requests
import json

import pandas as pd
import matplotlib.pyplot as plt

import argparse
import urllib.parse

import datetime

# get the args
parser = argparse.ArgumentParser("punctuality_chart.py", description="A script to plot the punctuality of a train every day.")
parser.add_argument("--train", help="The full train number to be checked. See bahn.expert for Regional Train full numbers", type=str)
parser.add_argument("--days", help="Number of days to look into the past", type=int, default=7)
parser.add_argument("--departure", help="The departure station name", type=str)
parser.add_argument("--arrival", help="The arrival station name", type=str)
args = parser.parse_args()
startdate = datetime.datetime.now().date() - datetime.timedelta(days=args.days-1) #zieht hier 1 zu viel ab.

# get the data

headers = {
    'authority': 'bahn.expert',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,de;q=0.7',
    'referer': 'https://bahn.expert/details/'+urllib.parse.quote_plus(args.train)+'/'+startdate.isoformat()+'T00:00:00.000Z?administration=801539',
}

date = []
for i in range(args.days): date.append(startdate + datetime.timedelta(days=i))
departure = []
arrival = []

for d in date:
    search_arrival = False

    params = {
        'initialDepartureDate': d.isoformat()+'T00:00:00.000Z',
        'administration': '801539',
    }
    response = requests.get(
        'https://bahn.expert/api/journeys/v1/details/'+urllib.parse.quote_plus(args.train),
        params=params, headers=headers
    )
    print(str(d.day) + ": " + str(response))

    responsejson = json.loads(response.content)

    for i in range(len(responsejson["stops"])):
        if not search_arrival and responsejson["stops"][i]["station"]["name"] == args.departure:
            # explainer:                                ⬇️ real time ⬇️ only the hour:minute timestamp
            departuretime = responsejson["stops"][i]["departure"]["time"][11:16]
            planneddeparturetime = responsejson["stops"][i]["departure"]["scheduledTime"][11:16]
            print("found departure time: " + departuretime)
            search_arrival = True
       
        elif search_arrival and responsejson["stops"][i]["station"]["name"] == args.arrival:
            arrivaltime = responsejson["stops"][i]["arrival"]["time"][11:16]
            plannedarrivaltime = responsejson["stops"][i]["arrival"]["scheduledTime"][11:16]
            print("found arrival time: " + arrivaltime)
            break

    departuretimeh = int(departuretime[:2]) + int(departuretime[3:])/60
    arrivaltimeh = int(arrivaltime[:2]) + int(arrivaltime[3:])/60

    departure.append(departuretimeh)
    arrival.append(arrivaltimeh)

planneddeparturetime = int(planneddeparturetime[:2]) + int(planneddeparturetime[3:])/60
plannedarrivaltime = int(plannedarrivaltime[:2]) + int(plannedarrivaltime[3:])/60

# plot the data

df_data = {'Category': date, 'Upper': departure, 'Lower': arrival}
df = pd.DataFrame(data=df_data)
df['Height'] = df['Upper'] - df['Lower']

ax = df.plot(kind='bar', y='Height', x='Category', bottom=df['Lower'],
             color='darkgreen', legend=False)
ax.axhline(0, color='black')
ax.set_ylim(6, 7) #sets the y range
ax.invert_yaxis()

ax.hlines(y=[planneddeparturetime,plannedarrivaltime], xmin=[0,0], xmax=[len(arrival),len(arrival)]) # hline for planned times

plt.tight_layout()
plt.show()
