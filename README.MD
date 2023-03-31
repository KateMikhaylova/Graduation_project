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

Для экспорта товаров доступна команда:
```
python manage.py export_goods
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

Для обеспечения доступа поставщиков к админке нужно убедиться, что is_staff и is_active необходимого пользователя является True, создать из под суперпользователя в админке группу с необходимыми доступами в разделе procurement_supply:

- Пользователь: can change, can view
- Категория: can add, can view
- Продукт: can add, can view
- Поставщик: can change, can view
- Характеристика: can add, can view
- Запас Продукта: can change, can view
- Характеристика запаса продукта: can add, can change, can view, can delete
- Закупщик: can view
- Розничный магазин: can view
- Корзина: can view
- Позиция корзины: can view
- Заказ: can view, can change
- Позиция заказа: can view, can change

и добавить в нее необходимых пользователей
