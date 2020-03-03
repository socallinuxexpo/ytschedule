# ytschedule

This application manages Youtube Live Streams for all day Confrence supporting multiple rooms and mutliple talks per room.

#### Requires
Python
```bash
apt-get install python-yaml libmysqlclient-dev

pip install pipenv
```


install daemon from https://github.com/socallinuxexpo/daemon-py.git

#### Getting Started

## Setup code
clone code then run:
```bash
pipenv install
pipenv shell
python manage.py migrate
python manage.py createsuperuser
```
## Get client_secret.json from Google
Go to: https://console.developers.google.com/apis/credentials
1. Click on new credentials and select "OAuth client id"
2. select other
3. set a name
4. click create button
4. click ok
5. Then click on the download button and save application_secrets.json in your working directory.

# Log app in to Youtube
```bash
python manage.py runscript login
```
Then go to the output url login and then past answer back into cli

# Populate data
Use fake data or signs method.

#### Set fake data
```bash
python manage.py runscript mktoday
```
#### Set from signs.xml
download signs.xml from SCALE website then run:
```bash
python manage.py runscript import_signxml
```

# Try the admin interface
```bash
python manage.py runserver
```
then point browser at http://localhost:8080/admin

# Try exporting a room to Youtube
```bash
python manage.py runscript publish_room
```

This will create a live stream and live broadcast for the Room and a live broadcast for each talk linked to the live stream for the Room.
