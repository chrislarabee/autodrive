import json
import os
from importlib import import_module

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


class API:
    """
    Connects to a Google Sheet using the appropriate configuration
    module from the sheets package.
    """
    def __init__(self, sheet_name):
        self.config = import_module('sheets._' + sheet_name)
        self.service = self._connect()

    def etl(self):
        """
        Uses the connection to the Google Sheets API to fetch the tabs
        specified in self.config.TABS, and then parse and save their
        data.

        :return: None
        """
        sheet_api = self.service.spreadsheets()

        for t, tab_data in self.config.TABS.items():
            # Get the values from the tab:
            print(f'Get values from {t}')
            rows, columns = self.fetch_sheet_data(
                t, tab_data[0], tab_data[1], sheet_api, self.config.SHEET_ID)
            dicts = self._create_dicts(columns, rows)
            # Get the Schema object for the tab:
            s = tab_data[3]
            # Use the Schema object to parse each row in dicts:
            parsed_dicts = [s.parse(d) for d in dicts]
            # Get the file path for the tab's parsed data:
            file_path = tab_data[2] + '/' + t
            self._save(file_path, parsed_dicts)
            print('--Values successfully downloaded and saved.')
            print(f'--Sample={parsed_dicts[0]}')

    @staticmethod
    def fetch_sheet_data(tab, range_token, header_row, sheet_api, sheet_id):
        """
        Collects the data from a specified tab in a Google sheet.

        :param tab: A string, the name of the tab to pull from.
        :param range_token: A string in the format of:
            start_column*:end_column (e.g. A*:C).
        :param header_row: An integer, the row number of the first row
            of data you want to collect.
        :param sheet_api: A Google Sheets connection object from
            self.service.spreadsheets().
        :param sheet_id: The id token of the Google Sheet (see the
            README for more info).
        :return: The rows and column header for the requested tab's
            data.
        """
        # Assemble the range:
        data_range = range_token.replace('*', str(header_row))
        r = tab + '!' + data_range

        # Get the data:
        result = sheet_api.values().get(spreadsheetId=sheet_id,
                                        range=r).execute()
        columns = result.get('values', [])[0]
        rows = result.get('values', [])[1:]

        if not rows:
            print(f'--No data found in {tab} in range {data_range}')

        return rows, columns

    @staticmethod
    def _create_dicts(columns, rows):
        """
        Converts a list of row lists and a list of column names into a
        list of dictionaries.

        :param columns: A list of strings.
        :param rows: A list of lists.
        :return: A list of dictionaries with columns as keys matched to
            corresponding row indices.
        """
        results = []
        for row in rows:
            row_dict = {}
            for i, r in enumerate(row):
                col = columns[i]
                row_dict[col] = r
            results.append(row_dict)
        return results

    @staticmethod
    def _connect():
        """
        Connects to the Google Sheets api.

        :return: The results of the connection attempt.
        """
        scopes = 'https://www.googleapis.com/auth/spreadsheets.readonly'

        # The file token.json stores the user's access and refresh
        # tokens, and is created automatically when the authorization
        # flow completes for the first time.
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', scopes)
            creds = tools.run_flow(flow, store)
        service = build('sheets', 'v4', http=creds.authorize(Http()))

        return service

    @staticmethod
    def _save(file_path, data):
        """
        Saves a list of dictionaries as a json to the provided path.
        Existing files of the same path will be overwritten.

        :param file_path: A string, which must be a valid file path
            without extension.
        :param data: A list of dictionaries.
        :return: None
        """
        f = file_path + '.json'
        if os.path.exists(f):
            os.remove(f)
        with open(f, 'a') as a:
            for d in data:
                a.write(json.dumps(d) + '\r')
