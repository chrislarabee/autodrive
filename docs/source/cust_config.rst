.. cust_config:

Custom Connection Configuration
===============================

Autodrive is designed to be fully customizable in terms of connection configuration. 
Anything that connects to your Google Drive or a Google Sheet can have its default 
connection behavior overridden. For most use-cases, simply having your credentials 
saved as a ``credentials.json`` file on your working directory will meet your needs, 
but for special cases, you can customize this functionality simply by instantiating 
your own :class:`~autodrive.interfaces.AuthConfig` and passing that to your Views,
:class:`Folders <autodrive.drive.Folder>`, or :class:`~autodrive.drive.Drive`.

Files
*****

For example, you can customize the path to your credentials file and where the
resulting token will get saved:

.. code-block:: python

    config = AuthConfig(
        token_filepath="custom_token.pickle",
        creds_filepath="/path/to/somewhere/else/creds.json"
    )


Environment Variables
*********************

You can also bypass the file-loading behavior entirely and inject your credentialling
information with environment variables:

.. code-block:: python

    # You can get these from your .pickle token after connecting for the first time:
    AUTODRIVE_TOKEN="your_token_here"
    AUTODRIVE_REFR_TOKEN="your_refresh_token_here"
    # You can find these in GCP or in your credentials.json file:
    AUTODRIVE_CLIENT_ID="your_client_id_value"
    AUTODRIVE_CLIENT_SECRET="your_client_secret"

If these variables are present in your environment, then Autodrive will automatically
detect them and use them to connect instead of looking for a file.

Config Dictionary
*****************

Finally, while it is probably not advisable, you can also pass your credentials 
directly to :class:`~autodrive.interfaces.AuthConfig` after loading them yourself:

.. code-block:: python

    config = AuthConfig(
        secrets_config={
            "client_id": "your_client_id_value",
            "client_secret": "your_client_secret",
            "token": "your_token_here",
            "refresh_token": "your_refresh_token_here"
        }
    )

.. warning::

    If you do need to use this option to load them for some reason, absolulely 
    do **NOT** put your credentials in your source code!
