# ytschedule

This application manages Youtube Live Streams for all day Confrence supporting multiple rooms and mutliple talks per room.

#### Requires
Python

pip install logstash_formatter
pip install pytz
pip install iso8601


#### Getting Started
clone code then run:

python manage.py migrate
python manage.py createsuperuser

# Pupulate data
download signs.xml from SCALE website then run:

script/import_signxml

# Try the admin interface
Run: python manage.py runserver

then point browser at http://localhost:8080/admin 

# Try exporting a room to Youtube
Run: script/publish_room.py

