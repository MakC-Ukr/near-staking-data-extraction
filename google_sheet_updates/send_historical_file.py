import os
import pandas as pd
from dotenv import load_dotenv
import pygsheets
import requests

load_dotenv()

def send_historical_file():
    base_dir_path = os.path.dirname(os.path.realpath(__file__))
    parent_dir_path = base_dir_path.split('/google_sheet_updates')[0] # This is the path to the parent directory of the google_drive_updates directory

    # connect to google sheeet
    client = pygsheets.authorize(service_file=f'{parent_dir_path}/service_credentials.json')
    sheet = client.open_by_key(os.getenv('HISTORICAL_GDS_FILE_ID'))
    wks = sheet.sheet1

    # find out the last epoch updated on google sheets
    cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
    last_epoch = int(cells[-1][0])
    print(f'Last updated epoch on google sheets: {last_epoch}')

    # compare the last epoch updated on google sheets with the last epoch updated on the historical_data/sc_avg file
    file = f'{parent_dir_path}/data/near_historical_gds.csv'
    historical_df = pd.read_csv(file)

    # identify rows that are new and need to be added to the google sheets file
    new_historical_df = historical_df[historical_df['epoch_height'] > last_epoch]
    print(f'new rows: {len(new_historical_df)}')

    # add new rows to google sheets file
    insert_into_row = len(cells)
    new_row = new_historical_df.values.tolist()
    wks = wks.insert_rows(insert_into_row, number=len(new_row), values= new_row)

if __name__ == '__main__':
    send_historical_file()