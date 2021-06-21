# All the keys and such that Google uses in its Drive and Sheets APIS that are
# relevant to Autodrive are listed here. If they ever change, it will be easy to
# change them here and alter all modules to reflect the update.

# General Google API query values:
FIELDS = "fields"
# Google Drive object property names:
ID = "id"
NAME = "name"
PARENTS = "parents"
# Google Sheet property names:
FILE_NAME = "title"
FILE_PROPS = "properties"
TABS_PROP = "sheets"
# Tab property names:
TAB_PROPS = "properties"
TAB_IDX = "index"
TAB_ID = "sheetId"
TAB_NAME = "title"
GRID_PROPS = "gridProperties"
COL_CT = "columnCount"
ROW_CT = "rowCount"
# Data property names:
DATA = "data"
ROWDATA = "rowData"
VALUES = "values"
FORMATTED_VAL = "formattedValue"
USER_ENTER_VAL = "userEnteredValue"
# Data types:
STRING = "stringValue"
FORMULA = "formulaValue"
NUMBER = "numberValue"
BOOLEAN = "boolValue"
DATA_TYPE_KEYS = [STRING, FORMULA, NUMBER, BOOLEAN]
TYPE_MAP = {
    STRING: str,
    FORMULA: str,
    NUMBER: float,
    BOOLEAN: bool,
    bool: BOOLEAN,
    str: STRING,
    float: NUMBER,
    int: NUMBER,
}
# Requests:
ADDTAB = "addSheet"
# Update cell property names:
ROWS = "rows"
RNG = "range"
