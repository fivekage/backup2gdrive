# Backup2GDrive

Backup2GDrive is a simple tool to backup your files to Google Drive.

## Usage

Fill the environments variable required into a .env file and run the script:
> To find the variables required, see .env.example file

If you haven't installed Docker, install it:
> https://www.docker.com/get-docker

Pull the image:
> docker pull gchr.io/fivekage/backup2gdrive

Run the container:
> docker run --env-file .env -v /path/to/data:/data gchr.io/fivekage/backup2gdrive

Docker compose example:
```yaml
version: '3'
services:
   backup2gdrive:
      image: gchr.io/fivekage/backup2gdrive:latest
      env_file: .env # Path to the .env file, it can be .env.backup2gdrive if you want to use a different name
      volumes:
         - /path/to/data:/data
```

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