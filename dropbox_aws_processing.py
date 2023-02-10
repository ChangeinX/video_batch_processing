"""
Upload video to drobox
"""

import os
import sys

import dropbox
from dropbox.exceptions import ApiError
from dropbox.files import WriteMode

dropbox_access_token = ""

dir_path = ""


def upload_files_to_dropbox():
    # Adapted from:
    # https://github.com/dropbox/dropbox-sdk-python/blob/master/example/back-up-and-restore/backup-and-restore-example.py
    for files in os.listdir(dir_path):
        if files.endswith(".mp4"):
            with dropbox.Dropbox(dropbox_access_token) as dbx:
                with open(os.path.join(dir_path, files), "rb") as f:
                    # We use WriteMode=overwrite to make sure that the settings in the file
                    # are changed on upload
                    print("Uploading " + files + " to Dropbox as " + files + "...")
                    try:
                        dbx.files_upload(
                            f.read(), "/" + files, mode=WriteMode("overwrite")
                        )
                    except ApiError as err:
                        # This checks for the specific error where a user doesn't have
                        # enough Dropbox space quota to upload this file
                        if (
                            err.error.is_path()
                            and err.error.get_path().error.is_insufficient_space()
                        ):
                            sys.exit("ERROR: Cannot back up; insufficient space.")
                        elif err.user_message_text:
                            print(err.user_message_text)
                            sys.exit()
                        else:
                            print(err)
                            sys.exit()


upload_files_to_dropbox()
