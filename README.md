# MasterBot
CW Master Castle Bot

# Trello taskboard:
[ТЫЦ](https://trello.com/b/mIKI2omk/%D1%81%D1%83%D0%BC%D1%80%D0%B0%D0%BA%D0%BE%D0%B1%D0%BE%D1%82)

### installation into venv (recommended):
```
virtualenv -p python3 .env #make sure you creating python3 venv
source .env/bin/activate
python3 -m pip install -r requirements.txt
```

### mysql database setup (only mysql is supported):

1)Install recent mysql-server distribution
e.g. for GNU/Linux:
```
sudo apt-get install mysql-server
```
2)create a root user (if it was not created during installation process)
```
sudo mysqladmin -u root password 'mynewpassword'
```
3)login to mysql as root:
```
sudo mysql -u root -h localhost -p
```
4)create a new user:
```
CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'mypass';
```
5)grant privileges to the new user:
```
GRANT ALL PRIVILEGES ON * . * TO 'myuser'@'localhost';
exit
```
6)log in to your new user similarly to step (3).

7)create a new database
```
CREATE DATABASE 'test';
```
8)exit to CLI
```
exit
```
9)open the file 'config.py.sample', enter your new database user's credentials, database name and your telegram bot API token

10)launch the bot:
```
python3 main.py
```
the mysql database schema will be created automatically by a built-in script.
