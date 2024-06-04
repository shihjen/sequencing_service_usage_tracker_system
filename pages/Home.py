# load the required dependencies
import streamlit as st
from streamlit_lottie import st_lottie
import json
import pandas as pd
import pymupdf
import fitz 
import helper
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from navigation import make_sidebar

# Streamlit page configuration
st.set_page_config(
    page_title='BCEAD Sequencing Services Usage Tracker System',
    page_icon=':chart_with_upwards_trend:',
    layout='wide',
    initial_sidebar_state='expanded'
)

make_sidebar()

################################################################################################################
# function to load the lottie file
def load_lottiefile(filepath: str):
    with open(filepath, 'r') as f:
        return json.load(f)

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

# function to update Google Sheet with DataFrame
def update_google_sheet(worksheet, data):
    # worksheet.clear()
    worksheet.update([data.columns.values.tolist()] + data.values.tolist())
#################################################################################################################

# load the lottie animation    
# lottie_cover = load_lottiefile('image/animation3.json')

st.title(':violet[BCEAD Sequencing Servies Usage Tracker]')
# st.lottie(lottie_cover, speed=0.6, reverse=False, loop=True, quality='low', height=800, key='first_animate')
st.sidebar.image('image/BCEAD.png')
st.sidebar.subheader(':violet[Welcome to the BCEAD Sequencing Services Usage Tracker System]', divider='gray')
st.sidebar.write('''
This application is designed to automate data extraction from Statement of Account (SoA) received for sequencing services ordered in the BCEAD laboratory. 
Simply upload the SoA, and the application will extract key information, including order ID, order date, 
user name, and number of sequencing reactions. 
You can choose to export this data in CSV format or push the extracted data directly into the database. 
For an overview of sequencing services usage in the BCEAD lab, please visit the dashboard page.
''')
st.sidebar.title('Upload File')
uploaded_file = st.sidebar.file_uploader('Upload the Statement of Account (SoA)', type='csv', accept_multiple_files=False)


################################################################################################################
# container - table display data extracted from the uploaded invoice(s)
container = st.container(border=True)
container.markdown('### Data Extracted from Statement of Account')

if uploaded_file is not None:
    #documents = []
    #for uploaded_file in uploaded_files:
        #doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        #documents.append(doc)

    #df = helper.process_pdf_directory(documents)
    #data = pd.DataFrame(df)
    data = pd.read_csv(uploaded_file)

try:
    processed_data = helper.process_csv(data)
    container.dataframe(processed_data)
    container.download_button(
    label=':floppy_disk: Download Dataset',
    data=processed_data.to_csv().encode('utf-8'),
    file_name=f'Sequencing_SOA.csv',
    mime='text/csv')
except:
    container.write('Upload invoice to extract information')

# get the existing records from the Google spreadsheet
credentials = authenticate_google_sheets_from_secrets()
spreadsheet_name = 'Sequencing_Records'
all_records = open_sheet(credentials, spreadsheet_name, 'All_Records')
records = sheet_to_dataframe(all_records)

# get a list of existing BioBasic order ID in the database
biobasic_id = list(records['Order_ID'][1469:].astype(str))

# filter the uploaded SOA for only records not in the database
try:
    processed_data_id = processed_data['Order_ID'].unique().tolist()
    new_id = set(processed_data_id) - set(biobasic_id)
    new_id_list = (list(new_id))
    data_to_push = processed_data[processed_data['Order_ID'].isin(new_id_list)]
    st.write(data_to_push)
except:
    pass

# submit button to push the data into database
try:
    button = st.sidebar.button('Push extracted data to the database')
    if button:
        with st.spinner('Upload data to the database...'):
            merged_df = pd.concat([records, data_to_push], axis=0)
            # update Google Sheet with combined DataFrame
            update_google_sheet(all_records, merged_df)
            st.success('Data successfully updated in the database!')
except:
    pass
