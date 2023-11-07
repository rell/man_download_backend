# Backend for MAN Download Tool

**_You must have database <ins>config.ini</ins> file in source directory with database credentials to run server_**

```ini
[database]
ENGINE = django.contrib.gis.db.backends.postgis
NAME = 
USER = 
PASSWORD = 
HOST = 
PORT = 5432

[django]
SECRET_KEY =
```

## Installation
RHEL:
Dependencies:
```bash
sudo yum imstall postgis33_15 postgresql15.x86_64 postgressql15-server postgresql-devel
````
