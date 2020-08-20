# Google Sheets API

This repository enables connection to Google Sheets, and stores Schemas for
the individual sheets as well as configuration of where to pull from and 
where to save to when the project is run for that sheet.

## General Setup

Setup a virtual environment (if desired) and install the requirements with: 
```
pip install -r requirements.txt
```

Follow the steps outlined here: 
https://developers.google.com/sheets/api/quickstart/python 
to prep your instance of python to connect to the Google Sheets API.

## Setup a Connection to a Sheet

Using the `sheets/_example.py` file as a guide, create a new python file in the 
sheets directory. You can name it whatever you want, but make sure the name is
not preceded by an _ (e.g. mynewfile.py not _mynewfile.py).

This file must declare two variables: SHEET_ID and TABS.

SHEET_ID is the id string of the Google Sheet you want to connect to. It can be 
found by opening the Google Sheet in your browser and copy pasting the alpha-numeric
string between 'https://docs.google.com/spreadsheets/d/' and '/edit#gid=...' in
the url.

TABS must be a dictionary:
* It can contain any number of keys, which must exactly
match the name(s) of the tab(s) in your Google Sheet that you want to download
from. You do not have to include a key for every tab in your Google Sheet, just
the ones you want to download from using the API.
* The value for each key in TABS must be a list or tuple. The instructions will
assume you're using a list for brevity.
* The first (index 0) value in the list must be a Google Sheets range of column
letters, with * as a wildcard character. For example, if you want to pull all 
values from Columns B through G from a tab, enter `'B*:G'`.
* The second value in the list must be an integer which corresponds to
the starting row you want to pull data from in the tab. For example, if you want 
to skip the first two rows in your tab, you would enter 3.
* The third value in the list must be a string, specifically a valid file path to
a directory where you want the data from this tab to be saved. You can create a
directory in the SheetsAPI repository or a directory somewhere else on your system.
* The fourth value must be a Schema object that has an attribute for every column
covered by the range you specified in the first value. The name of each attribute
must exactly match the column name. Refer to Schema Objects, below, for further
details on configure a Schema object.

Once you've configured SHEET_ID and TABS in your sheets module, you're ready to 
run the API's etl functionality.

## Running the API

To run the API, simply execute the main function of the SheetsAPI project and
pass the name of your sheets module as the parameter:
```
python ~/SheetsAPI/main.py --sheet=mynewfile
```

## Schema Objects

This is a brief high-level overview of Schema objects, which this API uses to
parse the data from each tab of your Google Sheet.

### Instantiating Schemas

Creating a Schema object is designed to be simple. All you need to do is
instantiate a Schema object in your sheet module for each tab you want to download
data from. The Schema object should be passed an argument for each column in the
data you're downloading, and the argument name must match the name of the column
exactly. 

The value of the argument can be a tuple:
```
s = Schema(
    colA=(int, 0)
)
```
The first value will be used as the data type, and the second value will be used
as the default value for rows with no value for that column.

Valid data types for Schema arguments include: `str, int, float, bool, list`. You 
can also pass `any` for columns that will have a variety of data types in them. 
The Schema object will do its best to parse `any` data appropriately, but will 
leave it as a string if it cannot figure out how to convert that row's data into 
the proper data type.
* Note that `list` has some special functionality. This will cause the Schema
to try to split the values in that column on commas (,) to create a python list
object. 

Instead of passing a tuple, you can pass just a data type:
```
s = Schema(
    colA=(int, 0),
    colB=float
)
```

The default value for colB, in this case, will be `None`.

Finally, you can also just pass `None` as the data type, in which case the data
type will just be `str`.
```
s = Schema(
    colA=(int, 0),
    colB=float,
    colC=None
)
```
