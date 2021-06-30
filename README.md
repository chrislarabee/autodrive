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

## Custom Configuration
