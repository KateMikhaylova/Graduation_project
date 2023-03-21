Для запуска проекта необходимо:

- клонировать репозиторий:
```
git clone https://github.com/KateMikhaylova/Graduation_project.git
```
- заполнить файл с переменными окружения .env:
```
nano .env
```
- установить зависимости:
```
pip install -r requirements.txt
```
- создать миграции:
```
python manage.py makemigrations
```
- провести миграции:
```
python manage.py migrate
```
- запустить сервер:
```
python manage.py runserver
```

Для запуска тестов необходимо установить библиотеки из requirements_dev: 
```
pip install -r requirements_dev.txt
```
и выполнить команду:
```
pytest
```
Примеры запросов к API представлены в файле requests-examples.http