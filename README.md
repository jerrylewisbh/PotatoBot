# MasterBot
CW Master Castle Bot

# Trello taskboard:
https://trello.com/b/gFo4UASZ/botato-20

# Additional Information
* CW API v0.6: https://hackmd.io/s/Hk60PGm0z
* See STYLE.md for additional Style information

# Installation 
Create a `config.py` file based on the provided `config.py.sample` file. You'll need: 

* This bot requires Python 3.6 and the dependencies from requirements.txt
* A telegram bot from @botfather
* Access to the CW MQ *including* _deals queues 
 
## Installation into virtualenv (recommended):
```
virtualenv -p python3 .env #make sure you creating python3 venv
source .env/bin/activate
python3 -m pip install -r requirements.txt
```

## MySQL/MariaDB database setup (only mysql is supported):
1) Install MySQL or MariaDB on your machine or in a container
2) Create a database, user and grant that account access to the database
3) Enter credentials into your `config.py` file.

## Redis
You'll also need Redis for more volatile Data (for example CW Exchange).

1) Install Redis
2) Enter config into your `config.py` file.


## Additional dependencies
You might need to install `python3-tk` as an additional dependency

# Utilities
When the bot was stopped for a longer period it might be wise to clear the stored messages in the Queue. 
You can use utils/empty_queues.py for this purpose.

# Starting the bot
Start the bot with `python3 main.py`. 

The Database schema will be created automatically by a built-in script.
