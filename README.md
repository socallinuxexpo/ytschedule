# ytschedule

This application manages Youtube Live Streams for all day Confrence supporting multiple rooms and mutliple talks per room.

#### Requires
Python

pip install logstash_formatter
pip install pytz
pip install iso8601


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


