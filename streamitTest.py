#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 15:49:00 2019

@author: asbarton1
"""


import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

#Set df view options
pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 10000)

#%%

st.title("Baltimore City Crime Map")

@st.cache
def getData():
    data = pd.read_csv('./BPDCrimeData.csv')
    data.columns = map(str.lower, data.columns)
    data['crimedate'] = pd.to_datetime(data['crimedate'], utc=True)
    data['month'] = pd.to_datetime(data['crimedate']).dt.strftime('%m-%Y')
    data.dropna(subset=['latitude', 'longitude'], inplace=True)
    return data
   
    
data_load_state = st.text('Loading crime data...')
data = getData()
data_load_state.text('Loading crime data... Complete')

#%%

def monthSelector(data):
    current_month = [datetime.today().strftime('%m-%Y')]
    months = data['month'].unique().tolist()
    month = st.multiselect(
            "Which months would you like to see data for?",
            options=months, default=current_month
            )
    return month
    

def optionsSelector(data):
    options = data['description'].unique().tolist()
    
    option = st.multiselect(
            'Which crimes types would you like to see?',
            options=options,default=options
            )
    return option

option = optionsSelector(data)
month = monthSelector(data)

@st.cache
def getFilteredData(data, option,  month):
    filtered_data = data.loc[data['month'].isin(month)]
    filtered_data = filtered_data.loc[filtered_data['description'].isin(option)]
    return filtered_data


filtered_data = getFilteredData(data, option=option, month=month)

@st.cache
def crimeCounts(filtered_data):
    df = filtered_data.groupby(['description'])['crimecode'].count().reset_index()
    df.rename(columns={'description': 'Crime', 'crimecode': 'Count'}, inplace=True)
    df.sort_values(by='Count', inplace=True, ascending=False)
    return df
#%%
@st.cache
def YTDcrimeTrends(data, option):
    months = pd.date_range(start='2019-01-01', end=datetime.today(), freq='M')
    months = [i.strftime('%m-%Y') for i in months]
    trend_data = data.loc[data['description'].isin(option)]
    trend_data = trend_data.loc[trend_data['month'].isin(months)]
    trend_data = trend_data.groupby(['month','description'])['crimecode'].count().reset_index()
    trend_data.rename(columns={'description': 'Crime', 'crimecode': 'Count'}, inplace=True)
    
    return trend_data

    
#%%    
    

countsdf = crimeCounts(filtered_data)
trenddf = YTDcrimeTrends(data, option)

st.map(filtered_data)

fig = px.bar(countsdf, x='Crime', y='Count')
st.plotly_chart(fig)

fig2 = px.line(trenddf, x='month', y='Count', color='Crime')
st.plotly_chart(fig2)

dataShow = st.checkbox('Show Data')
if dataShow:
    st.dataframe(filtered_data)
    

