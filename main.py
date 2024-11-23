from utils.fetch_config import fetch_config
from business_logic.create_backup import create_backup, regroup_backups
from utils.logger import setup_logger
from logging import Logger, INFO
from typing import List
from datetime import date
import os
def main():
    # Setup logger
    logger: Logger = setup_logger(name="backup2gdrive", log_file="logs/backup2gdrive.log", level=INFO)
    logger.info("Starting Backup2GDrive script. \nFetch config...")

    # Fetch config
    try:
        config = fetch_config()
    except FileNotFoundError as e: 
        logger.error("File not found: %s", e)   
        exit(1) 
    except ValueError as e:
        logger.error("Invalid config file: %s", e)
        exit(2)

    logger.info("Config fetched successfully.")
    logger.debug("Config fetched: %s", str(config))
    logger.info("Starting backup process...")

    # Create backups
    archived_filepaths: List[str] = []
    for path_to_backup in config.paths_to_backup:
        archived_filepaths.append(create_backup(path_to_backup))

    # Regroup backups
    backups_dir = os.path.join(os.getcwd(), "backups")
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)
    regroup_backups(archived_filepaths, os.path.join(os.getcwd(), "backups", f"BACKUP_{config.project_name.upper()}_{date.today().strftime('%Y%m%d')}.zip"))
if __name__ == "__main__":
    main()
