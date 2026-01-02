# TeleSentry_V2

Search for messages/leaks in Telegram channels.
We will use a user account and utilize the api_id and api_hash of the user account.



# EASY INSTALL
Just Run
```
./install.sh
```

## Important Links!
- https://my.telegram.org/auth
- https://github.com/LonamiWebs/Telethon
- https://docs.aiohttp.org/en/stable/index.html

To see the api id and api hash:
- https://my.telegram.org/auth

Generate a requirements file automatically:
- https://stackoverflow.com/questions/31684375/automatically-create-file-requirements-txt

### Install requirements:

```
pip install -r requirements.txt
```

### .env file template:
```
API_ID="api id"
API_HASH="api hash"
DB_HOST="database ip (localhost)"
DB_USER="user"
DB_PASSWORD="database password"
DB_NAME="database name"
GROUP_ID="group id"
```

## Configure webserver:

Copy the folder that is inside web/ (telegram_webserver) to /var/www/html
