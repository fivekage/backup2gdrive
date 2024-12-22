# Backup2GDrive

Backup2GDrive is a simple tool to backup your files to Google Drive.

## Usage

### Create a Service Account

- Create a google cloud projet, then a google service account
- Generate a json service account key
- Download the service account key as a JSON file
- Copy the JSON file to the `config/` folder and rename it to `google-service-account.json`
- Set the environment variable `GOOGLE_SERVICE_ACCOUNT_JSON_PATH` to the path of the JSON file, otherwise the script will use the default path `config/google-service-account.json`

Fill the environments variable required into a .env file and run the script:
> To find the variables required, see .env.example file

Fill the config into a config.json file located in `config/` folder and run the script:
> To find the config, see config/config.example.json

If you haven't installed Docker, install it:
> https://www.docker.com/get-docker

Pull the image:
> docker pull gchr.io/fivekage/backup2gdrive

Run the container:
> docker run --env-file .env -v /path/to/data:/data -v /path/to/logs:/logs -v /path/to/config:/config gchr.io/fivekage/backup2gdrive

Docker compose example:
```yaml
version: '3'
services:
   backup2gdrive:
      image: gchr.io/fivekage/backup2gdrive:latest
      env_file: .env # Path to the .env file, it can be .env.backup2gdrive if you want to use a different name
      volumes:
         - /path/to/data:/data
         - /path/to/logs:/logs
         - /path/to/config:/config
```
> To find an example docker compose file, see `docker-compose.yml`

**Backups will be shared with mail address you defined in the config file**
**Once the process is finished, connect to your GDrive account and go to "Shared with me" to see the backup folder**

# Example inputs data

You can find example inputs data in `config.example.json` and `.env.example`

If you are using Windows, you have to define your config like this to avoid errors on '\\' characters: 

```json
{
   "folderPath": "C:\\Users\\sm\\Desktop\\dev\\backup2gdrive\\backups\\",
   "filterFile": ".*\\.md$",
   "zipName": "docs"
},
```

# Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)