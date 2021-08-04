.. format:

Formatting
==========

The :class:`Tabs <autodrive.tab.Tab>` and :class:`Ranges <autodrive.range.Range>` 
both have a suite of :mod:`Formatting <autodrive.formatting>` attributes, which 
provide a wide range of methods that, when called, add a request to update the 
connected Google Sheet's formatting once committed. They are grouped into three 
areas, ``cell``, ``grid``, and ``text``. These breakdowns are designed to make it 
as convenient as possible to locate the desired formatting you wish to apply right 
in your IDE.

Cell
****

Cell formatting methods update the features of the cell(s) targeted, providing 
easy ways to add backgrounds, borders, and the like:

.. code-block:: python

    # This will add conditional formatting to the whole tab that will make every 
    # other row have a different color:
    tab.format_cell.add_alternating_row_background(Color(0.5, 1, 0.5))

Grid
****

Grid formatting methods update the underlying grid of a tab, including the size of 
cells, the number of rows and columns, and other features of the Google Sheet:

.. code-block:: python

    # This will set the width of all columns in the tab to the width of their 
    # contents, as if you'd double-clicked on the right edge of the column 
    # divider:
    rng.format_grid.auto_column_width()

.. note::

    Not all formatting methods are duplicated between :class:`~autodrive.tab.Tab` 
    and :class:`~autodrive.range.Range`. For example, 
    :class:`Tab.format_grid <autodrive.formatting.format_tab.TabGridFormatting>` 
    provides a number of methods relating to inserting and deleting rows that 
    wouldn't make sense to apply to a :class:`~autodrive.range.Range`.

Text
****

Finally, text formatting methods update the textual formatting of the cell 
contents. This includes anything that can appear within the cell, so despite the
name, number formatting is also applied via text formatting methods:

.. code-block:: python

    from autodrive.interfaces import AccountingFormat

    # Will apply the "accounting" mask to any numeric contents in the cell(s):
    rng.format_text.apply_format(AccountingFormat)

Chaining
********

All the formatting methods return their parent Formatting object, so you can 
easily generate a bunch of different formatting requests by chaining methods
together:

.. code-block:: python

    (
        tab.format_grid
        .insert_rows(num_rows=5, at_row=10)
        .insert_rows(num_rows=1, at_row=40)
        .append_rows(num_rows=20)
    )

.. warning::

    When queueing multiple formatting requests at once, be aware that the Google
    API treats batched formatting updates on the same cells in a particular way.
    If the different requests have partially overlapping ranges, then the later 
    request will *remove* the formatting of any previous requests made to update 
    the overlapping cells' format. Essentially, this means that you should only 
    batch formatting requests together if they all affect the exact same range of 
    cells, or if they all affect completely different rnages of cells.

More Info
*********

There are many more methods provided by the :class:`Tab <autodrive.tab.Tab>` and 
:class:`Range <autodrive.range.Range>` objects' :attr:`format_cell`, 
:attr:`format_grid`, and :attr:`format_text` properties than are covered here. 
For a complete listing of the currently available methods, see the 
:mod:`Formatting <autodrive.formatting>` documentation.
