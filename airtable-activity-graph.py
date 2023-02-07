import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

# replace YOUR_TOKEN and YOUR_BASE_ID with your own values
AIRTABLE_TOKEN = "YOUR_TOKEN"
AIRTABLE_BASE_ID = "YOUR_BASE_ID"

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

def main():

    print("Making API call to AirTable..")
    headers = {
        'Authorization': f'Bearer {AIRTABLE_TOKEN}',
        'Content-Type': 'application/json'
    }
    url = f"{AIRTABLE_URL}/bridge-data-gathering"
    data = []
    response = requests.request("GET", url, headers=headers)
    for x in response.json().get('records'):
        x.update(x.get('fields'))
        x.pop('fields')
        data.append(x)
    df = pd.DataFrame(data)

    print("Processing Data..")
    dates = [dt.datetime.strptime(time[:10], "%Y-%m-%d").date() for time in df.loc[:, 'createdTime']]
    unique_dates = list(set(dates)) # list(set(*)) removes duplicates
    start = min(unique_dates)
    end = max(unique_dates)
    n_days = (end-start).days
    x = [end - dt.timedelta(days = x) for x in range(n_days)]
    y = [dates.count(date) for date in x]
    print(f"Average Uploads per Day: {len(dates)/len(x)}")
    plt.bar(x, y)
    plt.title('Daily River Image Uploads at Kornhausbrücke')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.gcf().autofmt_xdate()
    plt.yticks(range(min(y), max(y) + 1))
    plt.show()

    print("Saving Figure..")
    plt.savefig('Daily River Image Uploads at Kornhausbrücke.png')

    print("Done")

if __name__ == "__main__":
    main()
