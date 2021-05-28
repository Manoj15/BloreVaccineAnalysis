import pandas as pd
import streamlit as st
from copy import deepcopy
import matplotlib as mpl
mpl.use("agg")
from matplotlib.backends.backend_agg import RendererAgg
_lock = RendererAgg.lock
import plotly.express as px

import fetch_tweet


# -- Set page config
apptitle = 'Bangalore COVID-19 Vaccines Slot Availability Analysis'

st.set_page_config(page_title=apptitle, page_icon=":eyeglasses:")

# -- Default detector list
detectorlist = ['H1','L1', 'V1']

# Title the app
st.title('Bangalore COVID-19 Vaccines Slot Availability Analysis')


# Fetch Data from Twitter
# st.set_page_config(page_title=None, page_icon=None, layout='centered', initial_sidebar_state='auto')
# @st.cache
# Not working since heroku does not allow to scrape twitter
# def fetch_data():
#     # This function will only be run the first time it's called
#     fetch_tweet.fetch_data()

# fetch_data()


# Date Read
tweets_df2 = pd.read_csv('https://raw.githubusercontent.com/Manoj15/BloreVaccineAnalysis/main/app_data.csv')
tweets_df2['Datetime'] = pd.to_datetime(tweets_df2['Datetime'])

st.sidebar.markdown("## Data Filter")

#-- Select Hospital
hospitals = tweets_df2.groupby('Hospital_Name').Capacity.count().reset_index()
hospitals = hospitals.sort_values('Capacity', ascending = False)
select_hospital = st.sidebar.selectbox('Select Hospital to filter',
                                hospitals.Hospital_Name.unique())

# Time Series Plot for entire city
st.header('Slot Availability Till Date for Bangalore')
plot_df_1 = deepcopy(tweets_df2)
plot_df_1['Date'] = plot_df_1.Datetime.dt.date
plot_df_1 = plot_df_1.groupby('Date').Capacity.sum().reset_index()
fig1 = px.line(plot_df_1, x='Date', y="Capacity")
st.plotly_chart(fig1, clear_figure=True)

# Tree plot of hospital/zip code slot availability
plot_df_2 = tweets_df2.groupby(['zip_code', 'Hospital_Name']).Capacity.sum().reset_index()
fig2 = px.treemap(plot_df_2, path=['zip_code', 'Hospital_Name'], values='Capacity')
st.plotly_chart(fig2, clear_figure=True)

# Time Series plot of hospital wise 
st.header('Slot Availability Till Date for Hospital Selected')
plot_df_3 = tweets_df2[tweets_df2.Hospital_Name == select_hospital]
plot_df_3['Date'] = plot_df_3.Datetime.dt.date
plot_df_3 = plot_df_3.groupby('Date').Capacity.sum().reset_index()
fig3 = px.line(plot_df_3, x='Date', y="Capacity")
st.plotly_chart(fig3, clear_figure=True)

# Day of Week plot of Hospital wise
plot_df_4 = tweets_df2[tweets_df2.Hospital_Name == select_hospital]
plot_df_4['DayName'] = plot_df_4.Datetime.dt.day_name()
plot_df_4 = plot_df_4.groupby('DayName').Capacity.sum().reset_index()
fig4 = px.bar(plot_df_4, x='DayName', y='Capacity', category_orders={'DayName':['Monday','Tuesday','Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']})
st.plotly_chart(fig4, clear_figure=True)

# Time of Day of Hospital Wise
plot_df_5 = tweets_df2[tweets_df2.Hospital_Name == select_hospital]
plot_df_5['HourofDay'] = plot_df_5['Hour']
plot_df_5 = plot_df_5.groupby('HourofDay').Capacity.sum().reset_index()
fig5 = px.bar(plot_df_5, x='HourofDay', y='Capacity', category_orders={'DayName':[str(i) for i in range(0, 25)]})
st.plotly_chart(fig5, clear_figure=True)

st.subheader('Please Note : Just for Educational Purposes. Use with Caution')