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
and specified target folders:

.. code-block:: python

    from autodrive import Folder

    f1 = Folder("folder_id_1")
    f2 = Folder("folder_id_2")

    drive.upload_files(
        ("path/to/a/file.txt", f2),     # This file will be uploaded to Folder f2.
        ("path/to/a/image.png", f1),    # This file will be uploaded to Folder f1.
        "path/to/a/spreadsheet.xlsx",   # This file will be uploaded to the root.
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
