import snscrape.modules.twitter as sntwitter
import pandas as pd

import re
from datetime import datetime
from dateutil import tz
import pytz

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def get_IST(date):
    
    gmt = pytz.timezone('GMT')
    eastern = tz.tzlocal()
    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S+00:00')

    dategmt = gmt.localize(date)
    date_ist = dategmt.astimezone(eastern)
    return str(date_ist)

def preprocess(df):
    
    # Filter only tweets containing vaccine info by using keywords like "available for 18 to 44" as the user only tweeets for that
    df = df[df.Text.str.contains("available for 18 to 44")]
    
    # Date
    df['Datetime']  =  df['Datetime'].apply(lambda x : get_IST(str(x)))
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%Y-%m-%d %H:%M:%S')
    
    # Vaccine (looks like this field started after sometime)
    df['Vaccine'] = df.Text.apply(lambda x : 'COVAXIN' if 'COVAXIN' in x else ('COVISHIELD' if 'COVISHIELD' in x else ''))
    df = df[df.Vaccine.notna()]
    
    # Zip Code
    df['zip_code'] = df.Text.apply(lambda x : re.match('\d{6}', x).group(0))
    
    # Hospital Name
    df['Hospital_Name'] = df.Text.apply(lambda x :  re.search('at (.+?)\(', x).group(0).replace('at ', '').replace('(', ''))
    df['Hospital_Name'] = df.Hospital_Name.apply(lambda x : x.split('on')[0][:-1])
    
     # Capacity(WIP)
    # df['Capacity'] = df.Text.apply(lambda x :   re.search('Capacity: (.+?),', x).group(0).replace(',', '').replace('Capacity: ',''))
    df['Capacity'] = df.apply(lambda x: re.findall(r'\d+', (x.Text.split(x['Hospital_Name'])[1]).split('(')[1]) if x['Hospital_Name'] != '' else x, axis = 1)
    df = df[df.Hospital_Name != '']
    df['Capacity'] = df.Capacity.apply(lambda x: x[0] if len(x) > 0 else -999)
    df = df[df.Capacity != -999]
    
    # Get time attributes
    df['Hour'] = df['Datetime'].dt.hour
    df['Day'] = df['Datetime'].dt.day
    df['dayofweek'] = df['Datetime'].dt.dayofweek
    
    df = df.reset_index(drop = True)

    return df

if __name__ == '__main__':
    # Creating list to append tweet data
    tweets_list1 = []

    # Using TwitterSearchScraper to scrape data and append tweets to list
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper('from:BloreVaccine' +  ' lang:en' + ' -filter:links -filter:replies').get_items()):
        tweets_list1.append([tweet.date, tweet.id, tweet.content, tweet.username])
        
    # Creating a dataframe from the tweets list above 
    tweets_df1 = pd.DataFrame(tweets_list1, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])

    tweets_df2 = preprocess(tweets_df1)

    tweets_df2.to_csv('app_data.csv', index = False)