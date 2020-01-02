from lib.schema import Schema

SHEET_ID = 'The string that comes between ' \
           'https://docs.google.com/spreadsheets/d/ and /edit#gid='

ROOT_DIR = 'C:/target/directory/location'

tab_schema = Schema(
    colA=None,
    colB=('int', 1),
    colC=('bool', False)
)

TABS = {
    'tab_name': ['A*:C', 1, ROOT_DIR + 'sub_directory', tab_schema]
}