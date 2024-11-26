import os
import re
import shutil
import tempfile
import zipfile

from models.files_to_backup import FilesToBackup


def create_backup(path_to_backup: FilesToBackup):
    """
    Creates a backup of files in the specified directory that match a given regex pattern.

    Parameters
    ----------
    path_to_backup : FilesToBackup
        An object containing the path of the folder to backup, the regex to filter files,
        the name for the output zip file, and optionally, the Google Drive destination path.

    Raises
    ------
    TypeError
        If path_to_backup is not a FilesToBackup object.
    FileNotFoundError
        If the specified folder path does not exist.

    Returns
    -------
    str
        The path of the created zip archive.
    """
    if not isinstance(path_to_backup, FilesToBackup):
        raise TypeError("path_to_backup must be a FilesToBackup object")

    if not os.path.exists(path_to_backup.folder_path):
        raise FileNotFoundError(f"Folder {path_to_backup.folder_path} does not exist")

    # Group all files that match the regex in a temp folder
    temp_folder = tempfile.TemporaryDirectory()
    files = [
        f
        for f in os.listdir(path_to_backup.folder_path)
        if re.match(path_to_backup.filter_file, f)
    ]
    for file in files:
        shutil.copy2(os.path.join(path_to_backup.folder_path, file), temp_folder.name)

    # Then zip the temp folder
    fullpath_output_zip = os.path.join(
        path_to_backup.folder_path, path_to_backup.zip_name
    )

    archived = shutil.make_archive(fullpath_output_zip, "zip", temp_folder.name)
    temp_folder.cleanup()

    return archived


def regroup_backups(list_of_backups: list[str], destination_path: str) -> None:
    """
    Regroups a list of backup zip files into a single zip file.

    Parameters
    ----------
    list_of_backups : list[str]
        A list of paths to backup zip files.

    destination_path : str
        The path to the destination zip file.

    Returns
    -------
    None
    """
    with zipfile.ZipFile(destination_path, "w") as zip_file:
        for backup in list_of_backups:
            zip_file.write(backup, os.path.basename(backup))

    for backup in list_of_backups:
        os.remove(backup)
