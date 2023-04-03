Для запуска проекта необходимо:

- клонировать репозиторий:
```
git clone https://github.com/KateMikhaylova/Graduation_project.git
```
- дозаполнить файл с переменными окружения .env (почта и приложение vk):
```
nano .env
```

- запустить docker compose:
```
sudo docker compose up --build -d
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

Схема и интерфейс DRF-Spectacular доступны на роутах
```
api/schema/
api/schema/swagger-ui/
api/schema/redoc/
```

Авторизация через VK доступна на роуте
```
accounts/vk/login/
```

Для обеспечения доступа поставщиков к админке нужно убедиться, что is_staff и is_active необходимого пользователя является True, создать из под суперпользователя (при запуске контейнера создается суперпользователь с паролем StrongPassword1! и именем admin) в админке группу с необходимыми доступами 
в разделе procurement_supply:
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

в разделе admin
- Import stocks: can add, can view

и добавить в группу необходимых пользователей.

Импорт товаров из админки осуществляется на роуте
```
admin/admin/importstocks/
```

Импорт товаров из API и из админки реализован через celery-задачу. При импорте возвращается id задачи. Для получения результатов выполнения можно отправить GET-запрос на роут 
```
import/task_id/
```