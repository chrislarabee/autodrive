.. output:

Simple Output
=============

Autodrive offers some simple output functionality for creating csv and json files
from the data in your :class:`~autodrive.range.Range`, :class:`~autodrive.tab.Tab`, 
and :class:`~autodrive.gsheet.GSheet` objects.

Outputting Ranges and Tabs
**************************

Outputting the fetched data for :class:`~autodrive.range.Range` and 
:class:`~autodrive.tab.Tab` objects is quite easy, all you really need to do is 
specify a path to write to:

.. code-block:: python

    tab.to_csv("path/to/your/file.csv")
    # Optionally you can insert a header row:
    tab.to_csv("path/to/your/file.csv", header=["column_a", "column_b", "column_c"])

    tab.to_json("path/to/your/file.json")
    # For to_json, you can specifiy the header row manually or with an index 
    # in the data:
    tab.to_json("path/to/your/file.json", header=["column_a", "column_b", "column_c"])
    tab.to_json("path/to/your/file.json", header=2)  # for the data in the 3rd row:

Outputting GSheets
******************

Outputting :class:`~autodrive.gsheet.GSheet` objects is only slightly more 
complicated. If you only specify a path to a directory (not a file), then every 
:class:`~autodrive.tab.Tab` in the :class:`~autodrive.gsheet.GSheet` will be 
output as individual files. For example, if you have an object with three tabs 
(named ``Sheet1``, ``Sheet2``, and ``Sheet3``), then this will output 3 files:

.. code-block:: python

    import os

    gsheet.to_csv("path/to/a/directory")
    gsheet.to_json("path/to/a/directory")

    os.listdir("path/to/a/directory")
    """
    [
        "path/to/a/directory/Sheet1.csv", 
        "path/to/a/directory/Sheet1.json", 
        "path/to/a/directory/Sheet2.csv",
        "path/to/a/directory/Sheet2.json", 
        "path/to/a/directory/Sheet3.csv", 
        "path/to/a/directory/Sheet3.json",
    ]
    """

Overriding Filenames
####################

By default, the files will be named the same as the corresponding tab titles, but 
you can override this behavior:

.. code-block:: python

    # Only the tab names you pass will be overridden:
    gsheet.to_csv(
        "path/to/a/directory", 
        filename_overrides={"Sheet1": "sums", "Sheet2": "averages"}
    )
    gsheet.to_json(
        "path/to/a/directory", 
        filename_overrides={"Sheet1": "sums"}
    )

    os.listdir("path/to/a/directory")
    """
    [
        "path/to/a/directory/sums.csv", 
        "path/to/a/directory/sums.json", 
        "path/to/a/directory/averages.csv",
        "path/to/a/directory/Sheet2.json", 
        "path/to/a/directory/Sheet3.csv", 
        "path/to/a/directory/Sheet3.json",
    ]
    """

Headers and Tab Subsets
#######################

You can also simultaneously limit the specific tabs output and/or set the header(s)
output with each file:


.. code-block:: python

    # If you specify any Tab names as kwargs, only the tabs you specify will be
    # output:
    gsheet.to_csv(
        "path/to/a/directory", 
        filename_overrides={"Sheet1": "sums"},
        Sheet1=["column_a", "column_b", "column_c"],
        Sheet2=None  # use None to output Tabs even if you don't supply a header.
    )
    gsheet.to_json(
        "path/to/a/directory", 
        Sheet3=["column_a", "column_b", "column_c"],
        Sheet2=0  # For to_json you MUST specify a header, or pass an index.
    )

    os.listdir("path/to/a/directory")
    """
    [
        "path/to/a/directory/Sheet1.csv", 
        "path/to/a/directory/Sheet2.csv",
        "path/to/a/directory/Sheet2.json", 
        "path/to/a/directory/Sheet3.json",
    ]
    """
