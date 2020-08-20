import argparse

from lib.api import API

parser = argparse.ArgumentParser(
    'Run the SheetsAPI to connect to a Google Sheet configured in '
    'the sheets directory.'
)

parser.add_argument(
    '--sheet',
    required=True,
    help='The name of the module in sheets that contains the '
         'configuration information you want to use for this run.'
         'Do not include the initial _ in the passed argument.'
)

args = parser.parse_args()

print('Running Sheets API...')

a = API(args.sheet)
a.etl()

print(f'Run of Sheets API complete. Downloaded values saved to '
      f'{a.config.ROOT_DIR}')
