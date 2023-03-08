import pandas as pd
import numpy as np
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

# User config

filter_data = True
filter_window = 10


def main():

    print("Making API call to AirTable..")
    data = []
    table = Table(AIRTABLE_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
    table.all()

    for records in table.iterate():  # records is a list of dictionaries (one "records" per table I believe)
        # [{'id': [{}, ... ,{}]}, {'id': ..}, {'id': ..}, {'id': ..}]
        for record in records:
            data.append(record['fields'])
    df = pd.DataFrame(data)

    # Debug
    # print(df)
    # df.to_csv("data.csv")

    # Daily Participation on All Locations

    print("Processing Data..")
    dates = [dt.datetime.strptime(time[:10], "%Y-%m-%d").date()
             for time in df.loc[:, 'Created']]
    unique_dates = list(set(dates))  # list(set(*)) removes duplicates
    start = min(unique_dates)
    end = max(unique_dates)
    n_days = (end-start).days
    x = [end - dt.timedelta(days=x) for x in range(n_days)]
    y = [dates.count(date) for date in x]
    print(f"Average Uploads per Day: {len(dates)/len(x)}")
    plt.bar(x, y)
    plt.title('Daily River Image Uploads at All Locations')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y'))
    x_ticks_interval = round((end-start).days/9)
    print(x_ticks_interval)
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=x_ticks_interval))
    plt.gcf().autofmt_xdate()
    plt.yticks(range(min(y), max(y) + 1))
    plt.ylabel("Number of Uploads per Day")


    print("Saving Figure..")
    plt.savefig('daily-river-image-uploads-at-all-locations.png')

    # Daily Participation per Location

    # Collect all Locations
    locations = list(df.loc[:, 'Location'])
    unique_locations = list(set(locations))
    n_unique_locations = len(unique_locations)
    print(f"{n_unique_locations} unique locations found")

    # Create a dict with one key per location and an empty list as a value
    locations_participation_data = {}

    # Compute the daily participation as above for every location
    for location in unique_locations:
        # Find all time entries at the current location
        local_df = df.query(f"Location == '{location}'")
        # Get Upload Dates
        location_dates = [dt.datetime.strptime(
            time[:10], "%Y-%m-%d").date() for time in local_df.loc[:, 'Created']]
        # Count the number of uploads for every day
        locations_participation_data[location] = [
            location_dates.count(date) for date in x]
        # Apply averaging filter
        if filter_data:
            locations_participation_data[location] = np.convolve(
                locations_participation_data[location], np.ones(filter_window)/filter_window, mode='same').tolist()

    # Plot for every location
    fig, ax = plt.subplots()
    handles = []
    for idx, location in enumerate(unique_locations):
        handle, = ax.plot(x, locations_participation_data[location])
        handles.append(handle)

    fig.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y'))
    fig.gca().xaxis.set_major_locator(mdates.DayLocator(interval=x_ticks_interval))
    ax.tick_params('x', labelrotation=45)
    fig.subplots_adjust(bottom=0.2)
    ax.set_ylabel("Number of Uploads per Day")

    ax.legend(handles, unique_locations)

    fig.suptitle(
        f"Daily River Image Uploads by Location{', filtered' if filter_data else ''}")

    print("Saving Figure..")
    fig.savefig('daily-river-image-uploads-by-location.png')

    print("Done")
    plt.show()  # must come after any savefig, as it also clears the plots

if __name__ == "__main__":
    main()
