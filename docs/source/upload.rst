.. upload

Uploading Files
===============

Using :class:`~autodrive.drive.Drive` or :class:`~autodrive.drive.Folder`, you 
can easily upload any file Google Drive will accept via Autodrive. For example,
you can upload a bunch of files right to the root of your Google drive, like so.

.. code-block:: python

    from autodrive import Drive

    drive = Drive()

    drive.upload_files(
        "path/to/a/file.txt",
        "path/to/a/image.png",
        "path/to/a/spreadsheet.xlsx",
    )

Uploading to Folders
********************

You can also upload the files to arbitrary folders, and mix-and-match unspecified 
and specified target folders using FileUpload objects:

.. code-block:: python

    from autodrive import Folder, FileUpload

    f1 = Folder("folder_id_1")
    f2 = Folder("folder_id_2")

    drive.upload_files(
        FileUpload("path/to/a/file.txt", f2),   # Will upload to Folder f2.
        FileUpload("path/to/a/image.png", f1),  # Will upload to Folder f1.
        "path/to/a/spreadsheet.xlsx",           # Will upload to the root.
    )

If you're uploading to a single folder though, this approach is easier:

.. code-block:: python

    folder = Folder("folder_id_1")

    # All of these files will be uploaded to the same folder:
    folder.upload_files(
        "path/to/a/file.txt",
        "path/to/a/image.png",
        "path/to/a/spreadsheet.xlsx",
    )

Converting to Google Formats
****************************

You can also convert the files right to the appropriate Google Drive format 
during upload.

.. note:: 

    Google specifies how this conversion must work, so Autodrive will detect the
    type of the file you upload and use Google's rules to determine what Google
    format it should be converted to. You may get some unexpected results if you
    choose to convert a file that doesn't obviously correspond to a Google 
    format.

.. code-block:: python

    drive.upload_files(
        FileUpload("path/to/a/file.txt", convert=True),         # To Google Doc.
        "path/to/a/image.png",                                  # Format unchanged.
        FileUpload("path/to/a/spreadsheet.xlsx", convert=True), # To Google Sheet.
    )