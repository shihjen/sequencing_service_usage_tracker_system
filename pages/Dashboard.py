# import essential libraries
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import helper
from navigation import make_sidebar

# Streamlit page configuration
st.set_page_config(page_title='BCEAD Sequencing Records',
                   page_icon='',
                   layout='wide',
                   initial_sidebar_state='auto')

make_sidebar()

# define a custom css script
custom_css = """
<style>
.custom-metric-card {
    background-color: #FFE4B5; /* Change the color code to your desired background color */
    color: #000000; /* Change the text color code to your desired color */
    padding: 8px; /* Optional: Adjust padding as needed */
}
</style>
"""

st.title(':violet[BCEAD Sequencing Records]')
st.sidebar.image('image/BCEAD.png')
st.sidebar.subheader(':violet[Welcome to the BCEAD Sequencing Services Usage Tracker System]', divider='gray')
st.sidebar.write('''
This dashboard provides a comprehensive overview of the BCEAD lab's research funding usage on sequencing services. 
You can view expenses by year using the year selection box. 
Additionally, the usage of sequencing services by individual or group of the lab members can be viewed via the user selection box. 
''')

#####################################################################################################
# function to connect Google spreadhseet
def authenticate_google_sheets_from_secrets():
    secrets = st.secrets["gcp_service_account"]
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(secrets, scope)
    return credentials

# function to open the Google spreadsheet
def open_sheet(credentials, spreadsheet_name, sheet_name):
    client = gspread.authorize(credentials)
    spreadsheet = client.open(spreadsheet_name)
    sheet = spreadsheet.worksheet(sheet_name)
    return sheet

# function to convert the Google spreadsheet into pandas dataframe
def sheet_to_dataframe(sheet):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df
########################################################################################################

# get the Google spreadhseet for the data
spreadsheet_name = 'Sequencing_Records'
credentials = authenticate_google_sheets_from_secrets()
all_records = open_sheet(credentials, spreadsheet_name, 'All_Records')
df = sheet_to_dataframe(all_records)

# preprocess the data
# convert the column 'Order_Date' into datetime data type
df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%Y-%m-%d')

# extract/create 3 new columns --- year, month and day
df['Year'] = df['Order_Date'].dt.year
df['Month'] = df['Order_Date'].dt.month
df['Day'] = df['Order_Date'].dt.day

# selectbox for year selection
year_option = np.sort(df['Year'].unique()).tolist()
year = st.sidebar.selectbox('Select year', year_option)

# data subset from year
selected_data = df[df['Year'] == year]

# selectbox for user selection
known_user_df = selected_data[selected_data['User']!='Unknown']
user_option = known_user_df['User'].unique().tolist()
user = st.sidebar.multiselect('Select user(s)', user_option, user_option, placeholder='Please select at least an user')
selected_data_user = selected_data[selected_data['User'].isin(user)]

# divide the body into 3 columns
col1, col3, col4 = st.columns([2,2.5,2.5])

# obtain the key metrics from the data subset
key_metrics = helper.get_key_metrics(selected_data_user)
total_expenses = round(df['Number_Samples'].sum()*4.60, 2)
selected_year_exp = round(selected_data_user['Number_Samples'].sum()*4.60, 2)

# key metric card --- total expenses to date
col1.markdown(f'#### Total Expenses from {year_option[0]} to {year_option[-1]}')
# display the custom CSS
col1.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
col1.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 25px; font-weight: bold; margin: 0;">S$ {total_expenses} </p>
</div>
""", unsafe_allow_html=True)

# donut chart
col1.markdown('## ')
col1.markdown(f'#### Expenses in {year}')
donut = helper.plot_donut(selected_year_exp,total_expenses)
col1.plotly_chart(donut, theme='streamlit', use_container_width=True)

# key metrics based on selected year
col1.markdown(f'#### In Year {year}')
col11, col12 = col1.columns(2)


# key metric card 1 --- expenses in the selected year 
# display the custom CSS
col11.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
col11.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 18px;">Expenses</p>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">S$ {key_metrics[0]} </p>
</div>
""", unsafe_allow_html=True)

# key metric card 2 --- monthly average
# display the custom CSS
col11.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
col11.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 18px;">Monthly Average</p>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">S$ {key_metrics[1]} </p>
</div>
""", unsafe_allow_html=True)

# key metric card 3 --- daily average
# display the custom CSS
col11.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
col11.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 18px;">Daily Average</p>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">S$ {key_metrics[2]} </p>
</div>
""", unsafe_allow_html=True)

# key metric card 4 --- total number of orders
# display the custom CSS
col12.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
col12.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 18px;">Number of Orders</p>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">{key_metrics[3]} orders </p>
</div>
""", unsafe_allow_html=True)

# key metric card 5 --- total number of reactions
# display the custom CSS
col12.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
col12.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 18px;">Number of Sequencing Reactions</p>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">{key_metrics[4]} reactions </p>
</div>
""", unsafe_allow_html=True)

# key metric card 6 --- average reactions per order
# display the custom CSS
col12.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
col12.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 18px;">Average Sequencing Reaction per Order</p>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">{key_metrics[5]} reactions </p>
</div>
""", unsafe_allow_html=True)



##################################################################################################
# column 2 --- heatmap and barchart
col3.markdown(f'#### Number of Sequencing Reactions in {year}')
processed_inv = helper.preprocess_heatmap(df)
heatmap = helper.plot_heatmap(processed_inv,year)
col3.plotly_chart(heatmap, theme='streamlit', use_container_width=True)
col3.markdown(f'#### Breakdown by Month in Year {year}')
col5, col6 = col3.columns(2)
#col5.markdown('#### Number of Orders')
barchart = helper.plot_bar(selected_data_user, year)
col3.plotly_chart(barchart, theme='streamlit', use_container_width=True)
#col6.markdown('#### Number of Sequencing Reactions')
#col6.plotly_chart(barchart, theme='streamlit', use_container_width=True)
###################################################################################################



###################################################################################################
# column 3 --- bubble chart
col4.markdown('#### Number of Sequencing Reactions Run in Each Month by User')
try:
    bubble = helper.plot_bubble2(selected_data_user, year)
    col4.plotly_chart(bubble, theme='streamlit', use_container_width=True)
except:
    col4.warning('Select at least an user for viewing the bubble chart.')
###################################################################################################




