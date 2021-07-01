# Autodrive

Autodrive is designed to make it as easy as possible to interact with the Google
Drive and Sheets APIs via Python. It is especially designed to provide as much
assisstance as possible through intellisense hints and autocompletion, as well as
through thorough type checking and hinting. These features are currently optimized
for VSCode, which you can download <a href="https://code.visualstudio.com/">here</a>
if you wish. They should also work in other Python IDEs.

## Requirements

Python 3.8+

## Installation

## Google API Credentials

Follow the steps outlined in the Prerequisites section
<a href="https://developers.google.com/drive/api/v3/quickstart/python">here</a>.
Download and save the `credentials.json` file to the working directory you want to
use Autodrive in.

## First Connection

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
indicating you can close the process, you should see a `gdrive_token.pickle` file
added to the working directory you saved your `credentials.json` file in. Next time
you use an Autodrive element that needs to connect to your Drive, this token will
be used and you will not be prompted to authorize access again until it expires.

## Basic Usage

The `Drive` class provides methods for finding and creating objects in your Google
Drive, such as Folders or Sheets.

```
gsheet = drive.create_gsheet("my-autodrive-gsheet")
```

### Tabs

Because Google calls spreadsheets "Sheets", and also refers to the individual
sub-sheets in a spreadsheet as "Sheets", Autodrive refers to the sub-sheets as "Tabs"
for clarity.

### Autodrive GSheet Views

Autodrive provides three different views of a Google Sheet, the `GSheet`, which
contains properties of the sheet itself and all its `Tabs`. `Tabs` provide convenient
access to methods allowing you to manipulate values and formats of individual tabs.
Finally, `Range` represents a specific row-column range in a `Tab` (i.e. A1:C3), and
provides methods for altering the values and/or formats of that range alone.

All of these Views are somewhat interchangeable as well, in that you can access the
`Tabs` on a `GSheet` and manipulate parts of a `Tab` without creating a `Range`. They
are meant to be different tools for differently sized jobs.

## Custom Configuration

Autodrive is designed to be fully customizable in terms of configuration. Anything that
connects to your Google Drive or a Google Sheet can have its default connection
behavior overridden. For most use-cases, simply having your credentials saved as a
`credentials.json` file on your working directory will meet your needs, but for special
cases, you can customize this functionality simply by instantiating your own
`AuthConfig`.

For example, you can customize the path to your credentials file and where the
resulting token will get saved:

```
from autodrive import AuthConfig

config = AuthConfig(
    token_filepath="custom_token.pickle",
    creds_filepath="/path/to/somewhere/else/creds.json"
)
```

And you can bypass this behavior entirely and inject your credentialling
information with environment variables:

```
# You can get these from your .pickle token after connecting for the first time:
AUTODRIVE_TOKEN="your_token_here"
AUTODRIVE_REFR_TOKEN="your_refresh_token_here"
# You can find these in GCP or in your credentials.json file:
AUTODRIVE_CLIENT_ID="your_client_id_value"
AUTODRIVE_CLIENT_SECRET="your_client_secret"
```

It is probably not advisable, but in some cases you could also pass your
credentials directly to `AuthConfig`, or load the token & creds files yourself and
pass them to AuthConfig if you need to:

```
config = AuthConfig(
    secrets_config={
        "client_id": "your_client_id_value",
        "client_secret": "your_client_secret",
        "token": "your_token_here",
        "refresh_token": "your_refresh_token_here"
    }
)
```

Note that I do not endorse putting your credentials in source code! This is for
very special cases or dev environments only!
