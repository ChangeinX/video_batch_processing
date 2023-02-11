"""
Upload video to drobox
"""

import os
import sys

import dropbox
from dropbox.exceptions import ApiError
from dropbox.files import WriteMode

dropbox_access_token = "sl.BYq1dVLDFiRPvfhomFCtX7FX7G0fOKeHhOsHn1moY3XyVY8ccO7feEOd0k1OT0b1VNV1Mv-mofOeFPfvA5xaOcOe3h4nsZ4gissPntLTBewYTNKN92_DaoHHGOn7FGvKYdDu1rCE"

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


def get_entries_from_dropbox():
    dbx = dropbox.Dropbox(dropbox_access_token)
    entries = dbx.files_list_folder("").entries
    return entries


# list of file ids, and file names concurrently
def get_file_ids_and_names():
    entries = get_entries_from_dropbox()
    # zip file ids and file names to appear together
    file_ids = [entry.id for entry in entries]
    file_names = [entry.name for entry in entries]
    for file_id, file_name in zip(file_ids, file_names):
        print(file_id, file_name)


get_file_ids_and_names()
