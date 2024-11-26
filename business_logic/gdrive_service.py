import os

from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build, MediaFileUpload
from utils.human_readable_bytes import human_readable_bytes
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials
from typing import List, Optional
from utils.logger import get_logger


class GoogleDriveService:
    def __init__(self, users_emails: List[str]):
        """
        Initialize the GoogleDriveService class.

        Sets up the necessary scopes for Google Drive API access, initializes
        a logger for the service, and creates a Google Drive API service instance.
        """
        if not isinstance(users_emails, list) or not users_emails:
            raise ValueError("users_emails must be a non-empty list")
        self.SCOPES = ["https://www.googleapis.com/auth/drive"]
        self.logger = get_logger("backup2gdrive")
        self.service = self._create_service()
        self.users_emails = users_emails

    def check_storage_usage(self, storage_quota: dict) -> float:
        """
        Gets the storage usage of the Google Drive account.

        Parameters
        ----------
        storage_quota : dict
            A dictionary containing the storage quota information.

        Returns
        -------
        float
            The percentage of used storage.
        """
        # Convert usage to float
        usage_in_drive = human_readable_bytes(float(storage_quota["usageInDrive"]))
        limit = human_readable_bytes(float(storage_quota["limit"]))

        # Calculate the percentage of used storage
        self.logger.info(f"Google Drive storage usage: {
            usage_in_drive} / {limit}")

    def _create_service(self):
        """
        Authenticate with a service account and return a Google Drive API service instance.
        """
        service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON_PATH", None)
        credentials = Credentials.from_service_account_file(
            filename=service_account_path or "config/google-service-account.json",
            scopes=self.SCOPES,
        )
        drive_service = build("drive", "v3", credentials=credentials)
        about_info = drive_service.about().get(fields="user").execute()
        self.user_email = about_info.get("user").get("emailAddress")
        self.logger.info(f"Authenticated as {self.user_email}")

        about = drive_service.about().get(fields="storageQuota").execute()
        self.check_storage_usage(about.get("storageQuota"))

        return drive_service

    def create_folder_structure(self, gdrive_destination_path: List[str]) -> List[str]:
        """
        Create the specified folder structure on Google Drive.
        Returns a list of folder IDs corresponding to the created folder hierarchy.
        """
        folder_ids = []
        parent_id = None  # Start at root

        for folder_name in gdrive_destination_path:
            # Adjust query for root folder (no parent ID)
            query = f"name='{folder_name}' and trashed=false and mimeType='application/vnd.google-apps.folder'"
            if parent_id:  # Add parent constraint if not root
                query += f" and '{parent_id}' in parents"

            try:
                results = (
                    self.service.files()
                    .list(q=query, fields="files(id, name)")
                    .execute()
                )
                folders = results.get("files", [])
            except HttpError as error:
                self.logger.error(
                    f"Error searching for folder '{folder_name}': {error}"
                )
                raise

            if folders:
                # Folder exists, use its ID
                folder_id = folders[0]["id"]
                self.logger.info(f"Folder '{folder_name}' exists with ID: {folder_id}")
            else:
                # Folder doesn't exist, create it
                file_metadata = {
                    "name": folder_name,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [parent_id]
                    if parent_id
                    else [],  # Root or a parent folder
                }
                try:
                    folder = (
                        self.service.files()
                        .create(body=file_metadata, fields="id")
                        .execute()
                    )
                    folder_id = folder["id"]
                    self.logger.info(
                        f"Folder '{folder_name}' created with ID: {folder_id}"
                    )
                except HttpError as error:
                    self.logger.error(f"Error creating folder '{folder_name}': {error}")
                    raise

            if not folder_id:
                self.logger.error(f"Failed to create or find folder '{folder_name}'.")
                raise ValueError(f"Failed to create or find folder '{folder_name}'.")

            folder_ids.append(folder_id)
            parent_id = folder_id  # Next folder is a child of this one

        return folder_ids

    def remove_old_files(self, days_old: int = 30) -> int:
        """
        Remove old backup files from Google Drive.
        """
        # Get all files in the root folder
        results = (
            self.service.files()
            .list(
                q="mimeType != 'application/vnd.google-apps.folder' and trashed = false",
                spaces="drive",
                fields="files(id, name, modifiedTime)",
            )
            .execute()
        )
        files = results.get("files", [])

        # Filter out files older than the specified number of days
        filtered_files = [
            file
            for file in files
            if (
                datetime.now(timezone.utc)
                - datetime.fromisoformat(file["modifiedTime"])
            )
            > timedelta(days=days_old)
        ]

        # Delete the filtered files
        for file in filtered_files:
            self.service.files().delete(fileId=file["id"]).execute()
            self.logger.info(f"Deleted file '{file['name']}'")

        return len(filtered_files)

    def file_exists(self, file_name: str, parent_folder_id: str) -> bool:
        """
        Check if a file with the given name already exists in the specified folder.
        """
        if not parent_folder_id:
            self.logger.error(
                "Parent folder ID is None. Ensure the folder structure is created properly."
            )
            raise ValueError("Parent folder ID is None.")
        query = (
            f"name='{file_name}' and '{parent_folder_id}' in parents and trashed=false"
        )
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])
        if files:
            return True
        return False

    def upload_file(
        self, file_name: str, gdrive_destination_path: List[str]
    ) -> Optional[str]:
        """
        Upload a file to Google Drive into the specified folder structure.
        """
        folders_parents_ids = self.create_folder_structure(gdrive_destination_path)
        parent_folder_id = folders_parents_ids[-1]

        # Share the main folder with the specified user
        for user_email in self.users_emails:
            self.share_resource(folders_parents_ids[0], user_email)

        # Check if the file already exists in the target folder
        if self.file_exists(os.path.basename(file_name), parent_folder_id):
            self.logger.info(
                f"Skipping upload for '{file_name}', as it already exists in Google Drive."
            )
            return None

        try:
            file_metadata = {
                "name": os.path.basename(file_name),
                "parents": [parent_folder_id],
            }
            media = MediaFileUpload(file_name, resumable=True)
            uploaded_file = (
                self.service.files()
                .create(
                    body=file_metadata,
                    media_body=media,
                    fields="id, name, parents, webViewLink, webContentLink",  # project
                )
                .execute()
            )
            self.logger.info(str(uploaded_file))
            self.logger.info(f"File '{file_name}' uploaded successfully. ID: {
                             uploaded_file.get('id')}")

            self.set_file_permissions(uploaded_file.get("id"))
            return uploaded_file.get("id")

        except HttpError as error:
            self.logger.error(f"An error occurred during upload: {error}")
            raise

    def set_file_permissions(self, file_id: str):
        """Set file permissions to 'Anyone with the link'."""
        try:
            # Set permissions to make it public
            permission = {
                "type": "anyone",
                "role": "reader",  # Or 'writer' depending on your requirement
            }
            self.service.permissions().create(fileId=file_id, body=permission).execute()
            self.logger.info(f"Permissions for file {
                             file_id} set to 'Anyone with the link'")
        except HttpError as error:
            self.logger.error(f"An error occurred while setting permissions: {error}")
            raise

    def share_resource(
        self, resource_id: str, email_address: str, role: str = "reader"
    ):
        """
        Share a Google Drive resource with a specific user by email.

        Parameters
        ----------
        resource_id : str
            The ID of the Google Drive resource to share (file/folder).
        email_address : str
            The email address of the user to share the resource with.
        role : str, optional
            The permission role to be granted to the user. Default is 'reader'.

        Returns
        -------
        None
            This function does not return anything, but logs the sharing action
            or any errors encountered during the process.
        """
        try:
            # Check if the user already has access
            permissions = (
                self.service.permissions()
                .list(fileId=resource_id, fields="permissions(emailAddress, role)")
                .execute()
            )
            for permission in permissions.get("permissions", []):
                print(permission.get("emailAddress"))
                if str(permission.get("emailAddress")).lower() == email_address.lower():
                    self.logger.info(
                        f"Resource {resource_id} already shared with {email_address}."
                    )
                    return

            # Set the permissions
            permission = {
                # Type of user (can be user, group, domain, or anyone)
                "type": "user",
                # 'reader' (view), 'writer' (edit), or 'owner' (transfer ownership)
                "role": role,
                "emailAddress": email_address,  # The email address to share the file with
            }

            # Create a permission object and apply it
            self.service.permissions().create(
                fileId=resource_id, body=permission, fields="id"
            ).execute()
            self.logger.info(
                f"Resource {resource_id} shared with {email_address} as {role}."
            )

        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")
            return None
