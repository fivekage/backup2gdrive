from utils.validate import validate_path, validate_regex, validate_filename

class FilesToBackup:
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
      return f"FilesToBackup(folder_path={self.folder_path}, filter_file={self.filter_file}, zip_name={self.zip_name}, g_drive_destination_path={self.g_drive_destination_path})"

