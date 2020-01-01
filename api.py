import json
import os
import sys

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


class Schemer:
    """
    Organizes data rules (schema) for each spreadsheet in the google
    sheet and allows incoming data to be morphed to fit the schema
    of the sheet it came from.
    """
    def __init__(self):
        self.schema = {
            'stats': {
                'name': {'type': 'str', 'default': None},
                'code': {'type': 'str', 'default': None},
                'description': {'type': 'str', 'default': 'placeholder'}
            },
            'classes': {
                'name': {'type': 'str', 'default': None},
                'code': {'type': 'str', 'default': None},
                'description': {'type': 'str', 'default': 'placeholder'},
                'forest': {'type': 'int', 'default': 0},
                'mountain': {'type': 'int', 'default': 0},
                'river': {'type': 'int', 'default': 0},
                'plains': {'type': 'int', 'default': 0},
                'desert': {'type': 'int', 'default': 0},
                'str': {'type': 'int', 'default': 0},
                'agi': {'type': 'int', 'default': 0},
                'tou': {'type': 'int', 'default': 0},
                'cun': {'type': 'int', 'default': 0},
                'res': {'type': 'int', 'default': 0},
                'spi': {'type': 'int', 'default': 0},
                'requires': {'type': 'str', 'default': None},
                'tier': {'type': 'int', 'default': None},
                'roles': {'type': 'list', 'default': None}
            },
            'class_skills': {
                'class': {'type': 'str', 'default': None},
                'promotion': {'type': 'int', 'default': None},
                'name': {'type': 'str', 'default': 'Placeholder'},
            },
            'skills': {
                'name': {'type': 'str', 'default': None},
                'usage': {'type': 'str', 'default': None},
                'special': {'type': 'str', 'default': None},
                'description': {'type': 'str', 'default': 'placeholder'}
            },
            'status': {
                'name': {'type': 'str', 'default': None},
                'type': {'type': 'str', 'default': 'basic'},
                'rank': {'type': 'str', 'default': None},
                'trigger_func': {'type': 'str', 'default': None},
                'description': {'type': 'str', 'default': 'placeholder'},
            },
            'effects': {
                'entity_name': {'type': 'str', 'default': None},
                'targets': {'type': 'int', 'default': 'e'},
                'range': {'type': 'bool', 'default': False},
                'affects': {'type': 'list', 'default': ['all']},
                'power': {'type': 'int', 'default': 0},
                'shape': {'type': 'str', 'default': '1x1'},
                'does': {'type': 'str', 'default': None},
                'aspect': {'type': 'str', 'default': None},
                'value': {'type': 'int', 'default': -1},
                'apply_rate': {'type': 'float', 'default': None},
                'sets_to': {'type': 'any', 'default': None},
                'override': {'type': 'str', 'default': None},
                'consumes': {'type': 'str', 'default': None},
                'con_from': {'type': 'str', 'default': None},
                'con_rate': {'type': 'float', 'default': None},
                'triggers_on': {'type': 'str', 'default': None},
                'trigger_aspect': {'type': 'str', 'default': None},
            }
        }
        self.cur_schema = self.schema['classes']

    @staticmethod
    def _bool(val):
        """
        This is basically just a version of python's bool that actually
        converts the string to a boolean type correctly.

        :param val: A string.
        :return: val as a boolean, if convertible.
        """
        if val == 'FALSE':
            result = False
        elif val == 'TRUE':
            result = True
        else:
            raise ValueError('Cannot convert {} to bool'.format(val))
        return result

    @staticmethod
    def _convert(val, data_type):
        """
        Takes a string and a target data_type and attempts to convert it.

        :param val: A string.
        :param data_type: A string in [float, int, bool, any].
        :return: The converted val, or the original val if conversion failed.
        """
        conv_funcs = {
            'float': float,
            'int': int,
            'bool': Schemer._bool
        }
        output_val = val
        if data_type == 'any':
            for f in conv_funcs.values():
                result, output_val = Schemer._try_convert(val, f)
                if result:
                    break
        else:
            f = conv_funcs[data_type]
            result, output_val = Schemer._try_convert(val, f)
        return output_val

    @staticmethod
    def _try_convert(val, func):
        """
        Takes a string and uses func to try and convert it.
        :param val: A string.
        :param func: A data type conversion function.
        :return: A boolean indicating whether the conversion
            succeeded and either val or the converted val if
            successful.
        """
        if val is None:
            raise TypeError('_try_convert cannot accept None val.')
        try:
            result = func(val)
        except ValueError:
            return False, val
        else:
            return True, result
        
    def parse(self, row_dict):
        """
        Takes a piece of data (row_dict) and makes sure that it has all
        the keys in the currently selected schema. Applies schema rules
        to all values present in the data.
        """
        output_dict = {}
        for col, schema in self.cur_schema.items():
            data_type = self.cur_schema[col]['type']
            default = self.cur_schema[col]['default']        
            if col in row_dict.keys():
                val = row_dict[col]
                if val == '':
                    output_val = default
                else:
                    if data_type == 'list':
                        output_val = val.split(',')
                    elif data_type == 'str':
                        output_val = val
                    else:
                        output_val = Schemer._convert(val, data_type)
                output_dict[col] = output_val
            else:
                output_dict[col] = default
        
        return output_dict
        
    def rotate_schema(self, desired_schema):
        self.cur_schema = self.schema[desired_schema]
        

def connect():
    """
    Connects to the google sheet and returns the results of the
    connection attempt.
    """
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'

    # The file token.json stores the user's access and refresh
    # tokens, and is created automatically when the authorization
    # flow completes for the first time.
    store = file.Storage('data/token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    
    return service


def fetch_sheet_data(tab_data, service, SPREADSHEET_ID):
    """
    Retrieves data from the provided tab of the Google Sheet.
    """
    data_range = tab_data[1].replace('*', str(tab_data[2] + 1))
    col_range = tab_data[1].replace('*', str(tab_data[2])) + str(tab_data[2])

    # Call the Sheets API
    RANGE_NAME = tab_data[0] + data_range
    COLUMN_RANGE = tab_data[0] + col_range
    sheet = service.spreadsheets()
    # Get data in the table:
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])
    
    # Get data in the column headers from the table:
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=COLUMN_RANGE).execute()
    columns = result.get('values', [])[0]

    if not values:
        print('No data found.')

    return values, columns

  
# Saves a json, overwrites existing file if present.
def save_to_json(file_path, list_of_dicts):
    """
    Saves a json from a list of dictionaries to the specified path.
    Overwrites existing file if present.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'a') as a:
        for dict in list_of_dicts:
            a.write(json.dumps(dict) + '\r')


s = Schemer()


def create_data_dict(columns, data):
    """
    Converts the list of row list for a fetched datasheet into a list
    of dictionaries.
    """
    results = []
    for row in data: 
        row_length = len(row)
        row_dict = {}
        for i in range(0, row_length):
            col = columns[i]
            column_val = row[i]
            row_dict[col] = column_val
        results.append(row_dict)
    return results
  
  
def etl(spreadsheet_id, tabs, service):
    """
    Connects to a provided spreadsheet id and loops through the tabs in
    tabs, which must be a dictionary. 
    """
    for key, tab_data in tabs.items():
        print('Get values from %s' % (key))
        s.rotate_schema(key)
        try:
            values, columns = fetch_sheet_data(
                tab_data,
                service,
                spreadsheet_id)
                                               
            list_of_dicts = create_data_dict(columns, values)
            parsed_dicts = []
            for d in list_of_dicts:
                parsed_dicts.append(s.parse(d))
            file_path = 'data/' + tab_data[3] + '/' + key + '.json'
            save_to_json(file_path, parsed_dicts)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        else:
            print('Values successfully downloaded and saved.')


def main():
    
    game_id = '1Kxb_F63QrA4TvKbU5zTYyK54_8hkEdoIhgRZvteO9gc'
    
    service = connect()

    game_tabs = {'stats': ['stats!', 'A*:C', 1, 'game_data'],
                 'classes': ['class!', 'A*:Q', 4, 'class_data'],
                 'skills': ['skills!', 'A*:D', 1, 'class_data'],
                 'class_skills': ['class_skills!', 'A*:C', 1, 'class_data'],
                 'status': ['status!', 'A*:E', 1, 'class_data'],
                 'effects': ['effects!', 'A*:Q', 7, 'class_data']
    } 
           
    etl(game_id, game_tabs, service)
    
  
if __name__ == '__main__':
    main()
