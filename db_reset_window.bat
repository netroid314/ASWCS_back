del db.sqlite3
rmdir /s /q project\migrations
rmdir /s /q userauth\migrations
python manage.py makemigrations project
python manage.py makemigrations userauth
python manage.py migrate