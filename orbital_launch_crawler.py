import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import calendar
from re import search
from collections import OrderedDict 
import pandas as pd


def date_generator(start_date, end_date):
    '''
        Function for generating list of ISO 8601 dates for all days in the year 2019
    '''
    start = datetime.strptime(start_date, "%Y-%m-%d %z")
    end = datetime.strptime(end_date, "%Y-%m-%d %z")
    # list of datetime objects for all the days in 2019
    date_array = (start + timedelta(days=x) for x in range(0, (end-start).days))
    # dictionary for maintaining the orbital launch results predefined with keys as 
    # ISO 8601 dates and 0 as value
    date_dict = OrderedDict()
    for date in date_array:
        date_dict[str(date.isoformat())] = 0
    return date_dict

if __name__ == "__main__":

    year = "2019"
    # list for valid payloads report
    valid_stats = ['Successful', 'successful', 'operational', 'Operational', 'En Route', 'En route']
    # extracting orbital launch table
    website_url = requests.get('https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches').text
    soup = BeautifulSoup(website_url, 'lxml')
    table_body = soup.find('table', class_='wikitable collapsible').tbody

    counter = 0
    # variables for keeping track of distinct orbital launches
    valid_state_found = False
    curr_date = ""
    # generating dictionary of all the days in 2019 with initial launch values as 0
    date_dict = date_generator("2019-01-01 +0000", "2020-01-01 +0000")

    for row in table_body.find_all('tr'):
        counter = counter + 1
        # skipping the table headers
        if counter < 4:
            continue
        
        else:
            # extracting date data from rows
            date_data = row.find('td').find('span', class_='nowrap')
            
            if date_data:
                date_list = date_data.text.split(" ")
                # handling the case where the date includes a reference
                month = date_list[1].split('[')[0]
                if month:
                    date = year+"-"+month+"-"+date_list[0]+" +0000"
                    date_object = datetime.strptime(date, '%Y-%B-%d %z')
                    # setting flags for updating the orbital launch value
                    curr_date = str(date_object.isoformat())
                    valid_state_found = False
            
            # extracting outcome column for getting outcome of the launch
            else:
                # list of values having Decay and Outcome column
                temp_status = [stats.text for stats in row.find_all('td', {'rowspan' : '1'})]
                if len(temp_status) > 0:
                    # handling newline and reference condition of outcome
                    status = temp_status[-1].rstrip("\n\r").split('[')[0]
                    # skip the row if already a valid state is found
                    if valid_state_found == True:
                        continue
                    # updating the dictionary by incrementing value for the launch date
                    elif status in valid_stats:
                        date_dict[curr_date] = date_dict[curr_date] + 1
                        valid_state_found = True

    # exporting the result as csv
    result_df = pd.DataFrame(list(date_dict.items()), columns=['date', 'value'])
    result_df.to_csv("orbital_launch_data.csv", index=False)

