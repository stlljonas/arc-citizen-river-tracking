import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import config
from pyairtable import Api, Base, Table

# config.py file must exist and have valid values

AIRTABLE_BASE_ID = config.AIRTABLE_BASE_ID
AIRTABLE_KEY = config.AIRTABLE_KEY
AIRTABLE_TABLE_NAME = config.AIRTABLE_TABLE_NAME

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

def main():

    print("Making API call to AirTable..")
    data = []
    table = Table(AIRTABLE_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
    table.all()

    for records in table.iterate(): # records is a list of dictionaries (one "records" per table I believe)
        # [{'id': [{}, ... ,{}]}, {'id': ..}, {'id': ..}, {'id': ..}]
        for record in records:
            data.append(record['fields'])
    df = pd.DataFrame(data)

    # Debug
    # print(df)
    # df.to_csv("data.csv")

    print("Processing Data..")
    dates = [dt.datetime.strptime(time[:10], "%Y-%m-%d").date() for time in df.loc[:, 'Created']]
    unique_dates = list(set(dates)) # list(set(*)) removes duplicates
    start = min(unique_dates)
    end = max(unique_dates)
    n_days = (end-start).days
    x = [end - dt.timedelta(days = x) for x in range(n_days)]
    y = [dates.count(date) for date in x]
    print(f"Average Uploads per Day: {len(dates)/len(x)}")
    plt.bar(x, y)
    plt.title('Daily River Image Uploads at All Locations')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.gcf().autofmt_xdate()
    plt.yticks(range(min(y), max(y) + 1))

    print("Saving Figure..")
    plt.savefig('Daily River Image Uploads at All Locations.png')

    plt.show() # must come after savefig(), as it wipes the plot

    print("Done")

if __name__ == "__main__":
    main()
