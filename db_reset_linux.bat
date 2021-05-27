rm db.sqlite3
rm -rf ./credit/migrations
rm -rf ./project/migrations
rm -rf ./userauth/migrations
python manage.py makemigrations credit
python manage.py makemigrations project
python manage.py makemigrations userauth
python manage.py migrate