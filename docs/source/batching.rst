.. batching

Batch Updating and Requests
===========================

Wherever possible, Autodrive creates batches of update requests and collects them
within whatever View you call the relevant methods from. This is to minimize round
trips to the Google APIs and back, and give you full control over the timing and 
size of your interactions with the APIs.

.. note::

    Some methods (particularly on :mod:`Connection <autodrive.connection>` objects) 
    require that a request be sent to the Google APIs immediately. The documentation
    for the method will have a note (like this one) indicating this when a request
    will be sent upon execution.

All :meth:`write_values` methods on views and all methods provided by 
:mod:`Formatting <autodrive.formatting>` properties add a request to themselves or 
their parent view.  These requests can all be executed by calling the view's 
:meth:`commit` method. For example:

.. code-block:: python

    from autodrive import Tab

    # Adds a request to write the specified values to the tab:
    tab.write_values(
        [
            [1, 2, 3], 
            [4, 5, 6],
        ]
    )
    # Adds a request to have every other row have a colorful background:
    tab.format_cell.add_alternating_row_background(Color(0.5, 1, 0.5))
    # Adds a request to fit the width of the tab's columns to the width of their
    # values:
    tab.format_grid.auto_column_width()

    # All three of the above updates to the Tab can then be executed at once:
    tab.commit()

    # The commit() method sends the requests to the Google Sheets API and clears
    # the view's request queue:
    print(tab.requests)
    # []

.. note::

    If you're curious, you can examine the requests queued on a view through its
    :attr:`requests` property (as seen above). If you'll do, you'll note that the 
    requests are nothing more than dictionaries with all the relevant information 
    required by the Google Sheets API to process their updates. 
