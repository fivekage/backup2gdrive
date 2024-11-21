import json
import os
import re
from utils.validate import validate_path, validate_regex, validate_filename
# {
#    "projectName": "string",
#    "pathsToBackup": [
#       {
#          "folderPath": "string",
#          "filterFile": "regex",
#          "zipName": "string"
#       },
#       {
#          "folderPath": "string",
#          "filterFile": "regex",
#          "zipName": "string",
#          "gDriveDestinationPath": "string"
#       }
#    ],
#    "gDriveDestinationPath": "string"
# }

class PathToBackup:
   def __init__(self, folder_path: str, filter_file: str, zip_name: str, g_drive_destination_path: str):
      if not validate_path(folder_path):
         raise ValueError("folder_path must be a valid folder path")
      
      if not validate_regex(filter_file):
         raise ValueError("filter_file must be a valid regex")
      
      if not validate_filename(zip_name):
         raise ValueError("zip_name must be a valid zip filename")
      if g_drive_destination_path is not None:
         if not validate_path(g_drive_destination_path):
            raise TypeError("g_drive_destination_path must be a valid string folder path")

      self.folder_path = folder_path
      self.filter_file = filter_file
      self.zip_name = zip_name
      self.g_drive_destination_path = g_drive_destination_path

   def to_dict(self):
      return {
         "folderPath": self.folder_path,
         "filterFile": self.filter_file,
         "zipName": self.zip_name,
         "gDriveDestinationPath": self.g_drive_destination_path
      }
   
   def __str__(self):
      return f"PathToBackup(folder_path={self.folder_path}, filter_file={self.filter_file}, zip_name={self.zip_name}, g_drive_destination_path={self.g_drive_destination_path})"

class Config:
   def __init__(self, config: dict):
      if not isinstance(config, dict):
         raise TypeError("Config must be a dictionary")
      
      if "projectName" not in config or not isinstance(config["projectName"], str):
         raise KeyError("Config must contain a valid projectName key")
      
      if "pathsToBackup" not in config or not isinstance(config["pathsToBackup"], list):
         raise KeyError("Config must contain a pathsToBackup key")
      
      if "gDriveDestinationPath" not in config or not validate_path(config["gDriveDestinationPath"]):
         raise KeyError("Config must contain a gDriveDestinationPath key")
      
      
      self.project_name = config["projectName"]
      self.paths_to_backup = [_map_path_to_backup(path_to_backup) for path_to_backup in config["pathsToBackup"]]
      self.g_drive_destination_path = config["gDriveDestinationPath"]

   def to_dict(self):
      return {
         "projectName": self.project_name,
         "pathsToBackup": [path_to_backup.to_dict() for path_to_backup in self.paths_to_backup],
         "gDriveDestinationPath": self.g_drive_destination_path
      }

   def __str__(self):
      return f"Config(project_name={self.project_name}, paths_to_backup={self.paths_to_backup}, g_drive_destination_path={self.g_drive_destination_path})"


def _map_path_to_backup(path_to_backup: dict):
   return PathToBackup(
      folder_path=path_to_backup["folderPath"], 
      filter_file=path_to_backup["filterFile"], 
      zip_name=path_to_backup["zipName"], 
      g_drive_destination_path=path_to_backup.get("gDriveDestinationPath", None) # gDriveDestinationPath is optional
   )

def fetch_config() -> Config:
   current_dir = os.path.dirname(os.path.abspath(__file__))
   config_path = os.path.join(current_dir, '../config.json')
   if not os.path.exists(config_path):
      raise FileNotFoundError(f"Config file not found at {config_path}")
   with open(config_path, 'r') as config_file:
      config = json.load(config_file)
      
   return config