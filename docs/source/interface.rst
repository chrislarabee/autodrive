.. interface:

Interfaces
==========

Interfaces are essentially argument groupings that are consumed as parameters by
many different methods throughout Autodrive. They are designed to provide type 
hinting and checking, as well as data validation.  

Range Interfaces
****************

Range interfaces serve as guides to constructing valid start and end ranges for
a Google Sheet. They essentially correspond to a Google Sheets range like 
``A1:D50``. There are two types of range interfaces in Autodrive, 
:class:`FullRanges <autodrive.interfaces.FullRange>` and the less common
:class:`HalfRanges <autodrive.interfaces.HalfRange>`.

.. code-block:: python

    from autodrive.interfaces import FullRange, HalfRange

    # FullRanges are much more commonly used, and correspond to a grid of cells in
    # Google Sheets. For example, a FullRange covering cells from the upper-left-
    # most cell in a Google Sheet to the 4th column (D) and the 50th row could be
    # instantiated like:
    full = FullRange("A1:D50")

    # HalfRanges are less common, only being used by certain formatting methods. 
    # They represent a single row or column range in Google Sheets. For example,
    # you could select the entire top row of a Google Sheet with:
    half = HalfRange(start_idx="A", end_index="Z")  # A1:Z
    # Or you could select a part of a certain column:
    half = HalfRange(start_idx=1, end_index=50)  # A1:A50
    # Or the entire column:
    half = HalfRange(start_idx="A")  # A1

Formatting Interfaces
*********************

Formatting interfaces are fairly straightforward. They simply provide an easy, 
type-hinted way of helping you construct formatting update requests. 

.. code-block:: python

    from autodrive.interfaces import Color, TextFormat

    # You can easily instantiate a Color interface with RGBa color values:
    c = Color(235, 229, 52)  # hex: #ebe534

    # And TextFormat provides a guide for applying different fonts and the like:
    tf = TextFormat(bold=True, font_size=14, font="Calibri")


More Info
*********

For more information about the various interfaces, see the relevant 
:mod:`Interfaces <autodrive.interfaces>` Documentation.
