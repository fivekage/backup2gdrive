from utils.fetch_config import fetch_config
import logging

def main():
    logging.info("Starting Backup2GDrive script. \nFetch config...")
    try:
        config = fetch_config()
    except FileNotFoundError as e: 
        logging.error("File not found: %s", e)   
        exit(1) 

    print(config)

if __name__ == "__main__":
    main()
