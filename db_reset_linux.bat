rm db.sqlite3
rm -rf ./project/migrations
rm -rf ./userauth/migrations
python manage.py makemigrations project
python manage.py makemigrations userauth
python manage.py migrate