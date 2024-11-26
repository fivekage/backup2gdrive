from models.files_to_backup import FilesToBackup


class Config:
    def __init__(self, config: dict):
        if not isinstance(config, dict):
            raise TypeError("Config must be a dictionary")

        if "projectName" not in config or not isinstance(config["projectName"], str):
            raise KeyError("Config must contain a valid projectName key")

        if "pathsToBackup" not in config or not isinstance(
            config["pathsToBackup"], list
        ):
            raise KeyError("Config must contain a valid pathsToBackup key")

        if "gDriveDestinationPath" not in config:
            raise KeyError("Config must contain a valid gDriveDestinationPath key")

        if "daysToKeep" in config and not isinstance(config["daysToKeep"], int):
            raise TypeError("daysToKeep must be an integer")

        if "usersEmails" in config and not isinstance(config["usersEmails"], list):
            raise TypeError("usersEmails must be a list")

        self.project_name = config["projectName"]
        self.paths_to_backup = [
            self._map_path_to_backup(path_to_backup)
            for path_to_backup in config["pathsToBackup"]
        ]
        self.g_drive_destination_path = config["gDriveDestinationPath"]
        self.days_to_keep = config.get("daysToKeep", 7)
        self.users_emails = config.get("usersEmails", [])

    def _map_path_to_backup(self, path_to_backup: dict):
        """
        Maps a dictionary representing a path to backup to a FilesToBackup object.

        Parameters
        ----------
        path_to_backup : dict
           The dictionary representing a path to backup.

        Returns
        -------
        FilesToBackup
           The FilesToBackup object.
        """
        return FilesToBackup(
            folder_path=path_to_backup["folderPath"],
            filter_file=path_to_backup["filterFile"],
            zip_name=path_to_backup["zipName"],
            g_drive_destination_path=path_to_backup.get(
                "gDriveDestinationPath", None
            ),  # gDriveDestinationPath is optional
        )

    def to_dict(self):
        return {
            "projectName": self.project_name,
            "pathsToBackup": [
                path_to_backup.to_dict() for path_to_backup in self.paths_to_backup
            ],
            "gDriveDestinationPath": self.g_drive_destination_path,
        }

    def __str__(self):
        return f"Config(project_name={self.project_name}, paths_to_backup={[str(p) for p in self.paths_to_backup]}, g_drive_destination_path={self.g_drive_destination_path}), days_to_keep={self.days_to_keep}, users_emails={self.users_emails})"
