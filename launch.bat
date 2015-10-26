python.exe manage.py syncdb
python.exe manage.py makemigrations
python.exe manage.py migrate
start /b "SERVEUR VISIONNEUSE" python.exe manage.py runserver localhost:8001
timeout 1
start /MAX "" "%programfiles(x86)%\Google\Chrome\Application\chrome.exe" --new-window http://localhost:8001/