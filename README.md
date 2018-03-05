# ytschedule

This application manages Youtube Live Streams for all day Confrence supporting multiple rooms and mutliple talks per room.

#### Requires
Python
apt-get install python-yaml

pip install django==1.8.3<br />
pip install django_fsm<br />
pip install google-api-python-client
pip install django-json-response
pip install logstash_formatter
pip install pytz
pip install iso8601
pip install wakeonlan==0.2.2
pip install mysqlclient

pip install django==1.8.3 django_fsm google-api-python-client logstash_formatter pytz iso8601 wakeonlan==0.2.2 mysqlclient



install daemon from https://github.com/stackd/daemon-py/

#### Getting Started

## Setup code
clone code then run:

python manage.py migrate
python manage.py createsuperuser

## Get client_secret.json
Go to: https://console.developers.google.com/apis/credentials 
Click on new credentials and select "OAuth client id"
select other
set a name
then click create button
click ok
Then click on the download button and save client_serects.json in your working directory.


## Pupulate data
Use fake data or signs method.

# Set fake data
Run: script/mktoday.py

# Set from signs.xml
download signs.xml from SCALE website then run:

script/import_signxml

# Try the admin interface
Run: python manage.py runserver

then point browser at http://localhost:8080/admin 

# Try exporting a room to Youtube
Run: script/publish_room.py

This will create a live stream and live broadcast for the Room and a live broadcast for each talk linked to the live stream for the Room.


