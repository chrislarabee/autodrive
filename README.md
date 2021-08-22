# Autodrive

Autodrive is designed to make it as easy as possible to interact with the Google
Drive and Sheets APIs via Python. It is especially designed to provide as much
assistance as possible when writing code through hints and autocompletion, as well
as via thorough type checking and hinting. These features are currently optimized
for VSCode, which you can download <a href="https://code.visualstudio.com/">here</a>
if you wish. They should also work in other Python IDEs.

---

**Documentation:** https://autodrive-py.readthedocs.io/en/latest/

---

## Requirements

---

Python 3.8+

## Installation

---

### Google API Credentials

Follow the steps outlined in the Prerequisites section
<a href="https://developers.google.com/drive/api/v3/quickstart/python">here</a>.
Download and save the `credentials.json` file to the working directory you want to
use Autodrive in.

### First Connection

To test that your credentials provide the expected connection to your Google Drive
account, simply instantiate an Autodrive `Drive` instance:

```
from autodrive import Drive

drive = Drive()
```

If your credentials file was saved as `credentials.json`, your browser should
automatically open and prompt you to authorize the GCP project you created to
access your Google Drive. Click the various Allow prompts it will show you to
complete your first connection. After you see the browser switch to a page
indicating you can close the process, you should see a `gdrive_token.json` file
added to the working directory you saved your `credentials.json` file in. Next time
you use an Autodrive element that needs to connect to your Drive, this token will
be used and you will not be prompted to authorize access again until it expires.

## Quickstart

---

The `Drive` class provides methods for finding and creating objects in your Google
Drive, such as Folders or Sheets.

```
gsheet = drive.create_gsheet("my-autodrive-gsheet")
```

### Finding IDs

If you use `Drive` to search for your Sheets and Folders, you don't need to supply the
GSheet or Folder IDs yourself, but if you know exactly what Sheet you want, then you
can directly instantiate a GSheet or folder by pulling the necessary info from the
object's url.

For example, if your Sheet's url looks like this:

<p>
docs.google.com/spreadsheets/d/19k5cT9Klw1CA8Sum-olP7C0JUo6_kMiOAKDEeHPiSr8/edit#gid=0
</p>

Simply copy/paste the id (in green, above) between `/d/` and `/edit#` as the
`gsheet_id`:

```
from autodrive import GSheet

gsheet = GSheet(gsheet_id="19k5cT9Klw1CA8Sum-olP7C0JUo6_kMiOAKDEeHPiSr8")
```

> **Tabs:** Because Google calls spreadsheets "Sheets", and their api also refers
> to the individual sub-sheets in a spreadsheet as "Sheets", Autodrive instead
> refers to them as "Tabs" for clarity.

For a tab, you can get the `tab_id` from:

<p>
docs.google.com/spreadsheets/d/19k5cT9Klw1CA8Sum-olP7C0JUo6_kMiOAKDEeHPiSr8/edit#gid=234276686
</p>

```
from autodrive import Tab

tab = Tab(
    gsheet_id="19k5cT9Klw1CA8Sum-olP7C0JUo6_kMiOAKDEeHPiSr8",
    tab_title="Sheet2",
    tab_idx=0,
    tab_id=234276686
)
```

For a folder:

<p>
drive.google.com/drive/u/1/folders/1wLx-KMG2jO498xa5ZumB-SEpL-TwczZI
</p>

```
from autodrive import Folder

folder = Folder(folder_id="1wLx-KMG2jO498xa5ZumB-SEpL-TwczZI", name="Test Folder")
```

### Reading and Writing

You can easily download and write data from a Google Sheet using the `GSheet`,
`Tab`, or `Range` views.

```
# Fetches all the data in all cells of the tab:
tab.get_data()

# Writes 8 cells (2 rows of 4 columns, starting in cell A1) to the tab:
tab.write_values(
    [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
    ]
)
```

`GSheet` and `Range` have very similar methods, and all of them allow you to read
and write data to only a specific range in the Google Sheet. See the
<a href="https://autodrive-py.readthedocs.io/en/latest/">Documentation</a>
for more.
