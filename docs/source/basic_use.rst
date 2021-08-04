.. basic_use:

Basic Usage
===========

.. note::

    Because Google calls spreadsheets "Sheets", and also refers to the individual
    sub-sheets in a spreadsheet as "Sheets", Autodrive refers to the sub-sheets as 
    **Tabs** for clarity.

Autodrive is designed to be as easy to navigate right in your IDE as possible, with
broad type annotation to facilitate code completion. 

Interacting With Google Drive
*****************************

Autodrive's most basic class is the :class:`~autodrive.drive.Drive` class, which 
can be easily instantiated with your downloaded credentials.  With a 
:class:`~autodrive.drive.Drive` instance you can find and/or create files and 
folders in your Google Drive, or in shared drives if you have access to them. 

.. code-block:: python

    from autodrive import Drive

    # Simply instantiate a drive instance to authenticate using your saved credentials
    # file.
    drive = Drive()

    folder = drive.find_folder("Autodrive Folder")
    print(folder[0].name)
    # Autodrive Folder

Views
*****

Autodrive provides three different views of a Google Sheet, the 
:class:`~autodrive.gsheet.GSheet`, which contains properties of the sheet itself 
and all its :class:`Tabs <autodrive.tab.Tab>`. :class:`Tabs <autodrive.tab.Tab>` 
provide convenient access to methods allowing you to manipulate values and formats of
individual tabs.  Finally, :class:`~autodrive.range.Range` represents a specific 
row-column range in a :class:`~autodrive.tab.Tab` (i.e. A1:C3), and provides methods 
for altering the values and/or formats of that range alone.

These views are designed to be flexible, and you can use any of them to easily 
interact with the same part of the Google Sheet. For example, below is an example 
of instantiating a :class:`~autodrive.gsheet.GSheet`, :class:`~autodrive.tab.Tab`, 
and :class:`~autodrive.range.Range`, all of which would, for example, write values 
to the same cells of the Google Sheet:

.. code-block:: python

    from autodrive import GSheet, Tab, Range, FullRange

    gsheet = GSheet(gsheet_id="19k5cT9Klw1CA8Sum-olP7C0JUo6_kMiOAKDEeHPiSr8")
    # Calling write_values on gsheet will write the data to the first tab:
    gsheet.write_values(
        [
            [1, 2, 3, 4], 
            [5, 6, 7, 8],
        ]
    )

    tab = Tab(
        gsheet_id="19k5cT9Klw1CA8Sum-olP7C0JUo6_kMiOAKDEeHPiSr8",
        tab_title="Sheet1",
        tab_idx=0,
        tab_id=0
    )
    # Calling write_values on tab will write the data starting with cell A1:
    tab.write_values(
        [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
        ]
    )

    rng = Range(
        gsheet_range=FullRange("A1:Z1000"),
        gsheet_id="19k5cT9Klw1CA8Sum-olP7C0JUo6_kMiOAKDEeHPiSr8",
        tab_title="Sheet1",
    )
    # Calling_write values on rng will write the data starting with the first cell
    # in the Range:
    rng.write_values(
        [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
        ]
    )

.. note:: 

    **Integrating with Pandas**

    While Autodrive views cannot directly accept pandas DataFrames, DataFrames 
    provide methods to make it easy to convert them into a format accepted by
    Autodrive views:

    .. code-block:: python

        import pandas as pd

        df = pd.DataFrame([dict(a=1, b=2, c=3), dict(a=4, b=5, c=6)])

        # You can either pass the DataFrame as a list of lists:
        tab.write_values(df.values.tolist())

        # Or, if you want to automatically include the header, you can pass it 
        # as a list of dictionaries:
        tab.write_values(df.to_dict("records"))

As you can see, these views are nested within one each other as well, so if you 
have a :class:`~autodrive.tab.Tab` but want to create a :class:`~autodrive.range.Range`
off it for greater convenience, you can easily do so:

.. code-block:: python

    tab = gsheet.tabs["Sheet1"]

    rng = tab.gen_range(FullRange("G1:G"))
