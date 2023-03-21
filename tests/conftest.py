import pytest
from django.conf import settings
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from procurement_supply.models import (CartPosition, Category, ChainStore,
                                       Characteristic, Order, OrderPosition,
                                       Product, ProductCharacteristic,
                                       Purchaser, ShoppingCart, Stock,
                                       Supplier, User)

TEST_EMAIL = settings.EMAIL_HOST_USER


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin_auth():
    admin = User.objects.create(
        username="admin",
        email=TEST_EMAIL,
        first_name="name",
        last_name="surname",
        company="api",
        position="admin",
        is_superuser=True,
        is_staff=True,
        is_active=True,
        type="admin",
        password="Password1!",
    )
    return Token.objects.create(user_id=admin.id)


@pytest.fixture
def purchaser_auth():
    purchaser = User.objects.create(
        username="purchaser",
        email=TEST_EMAIL,
        first_name="name",
        last_name="surname",
        company="purchaser",
        position="purchaser",
        is_superuser=False,
        is_staff=False,
        is_active=True,
        type="purchaser",
        password="Password1!",
    )
    return Token.objects.create(user_id=purchaser.id)


@pytest.fixture
def supplier_auth():
    supplier = User.objects.create(
        username="supplier",
        email=TEST_EMAIL,
        first_name="name",
        last_name="surname",
        company="supplier",
        position="supplier",
        is_superuser=False,
        is_staff=False,
        is_active=True,
        type="supplier",
        password="Password1!",
    )
    return Token.objects.create(user_id=supplier.id)


@pytest.fixture
def user_factory():
    def factory(*args, **kwargs):
        return baker.make(User, *args, **kwargs)

    return factory


@pytest.fixture
def user_w_hashed_password():
    client = APIClient()
    data = {
        "username": "username1",
        "password": "StrongPassword1!",
        "email": TEST_EMAIL,
        "first_name": "first_name",
        "last_name": "last_name",
        "company": "company",
        "position": "position",
    }
    user = client.post("/api/v1/users/", data=data, format="json")
    response = client.post(
        "/api/v1/authorize/",
        data={"username": "username1", "password": "StrongPassword1!"},
        format="json",
    )
    token = response.json()["token"]
    return {
        "token": token,
        "user": user.json()["id"],
        "username": user.json()["username"],
        "password": data["password"],
    }


@pytest.fixture
def users_base():
    vegsupplier = User.objects.create(
        username="vegsupplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Иван",
        last_name="Иванов",
        company="Выборжец",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    grainsupplier = User.objects.create(
        username="grainsupplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Петр",
        last_name="Петров",
        company="Аладушкин",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )

    juice1supplier = User.objects.create(
        username="juice1supplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Николай",
        last_name="Николаев",
        company="Pepsico",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    juice2supplier = User.objects.create(
        username="juice2supplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Павел",
        last_name="Павлов",
        company="Мултон",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    breadsupplier = User.objects.create(
        username="breadsupplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Алексей",
        last_name="Алексеев",
        company="Каравай",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    admin = User.objects.create(
        username="admin",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Админ",
        last_name="Админов",
        company="Портал",
        position="админ",
        type="admin",
        is_superuser=True,
    )
    hypermarket = User.objects.create(
        username="hypermarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Ольга",
        last_name="Есенина",
        company="ОК",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )
    supermarket = User.objects.create(
        username="supermarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Ирина",
        last_name="Пушкина",
        company="5ка",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )
    minimarket = User.objects.create(
        username="minimarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Татьяна",
        last_name="Ахматова",
        company="Фасоль",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )
    micromarket = User.objects.create(
        username="micromarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Оксана",
        last_name="Фет",
        company="КиБ",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )

    token_vegsupplier = Token.objects.create(user=vegsupplier)
    token_grainsupplier = Token.objects.create(user=grainsupplier)
    token_juice1supplier = Token.objects.create(user=juice1supplier)
    token_juice2supplier = Token.objects.create(user=juice2supplier)
    token_breadsupplier = Token.objects.create(user=breadsupplier)
    token_admin = Token.objects.create(user=admin)
    token_hypermarket = Token.objects.create(user=hypermarket)
    token_supermarket = Token.objects.create(user=supermarket)
    token_minimarket = Token.objects.create(user=minimarket)
    token_micromarket = Token.objects.create(user=micromarket)

    Supplier.objects.create(
        user=vegsupplier, name="Выборжец", address="Выборг", order_status=True
    )
    Supplier.objects.create(
        user=grainsupplier,
        name="Аладушкин",
        address="Санкт-Петербург",
        order_status=False,
    )
    Supplier.objects.create(
        user=juice1supplier,
        name="Pepsico",
        address="Санкт-Петербург",
        order_status=True,
    )
    Supplier.objects.create(
        user=juice2supplier, name="Мултон", address="Санкт-Петербург", order_status=True
    )

    Purchaser.objects.create(user=hypermarket, name="ОК", address="Санкт-Петербург")
    Purchaser.objects.create(user=supermarket, name="5ка", address="Санкт-Петербург")
    Purchaser.objects.create(user=minimarket, name="Фасоль", address="Санкт-Петербург")

    return {
        "vegsupplier": token_vegsupplier,
        "grainsupplier": token_grainsupplier,
        "juice1supplier": token_juice1supplier,
        "juice2supplier": token_juice2supplier,
        "breadsupplier": token_breadsupplier,
        "admin": token_admin,
        "hypermarket": token_hypermarket,
        "supermarket": token_supermarket,
        "minimarket": token_minimarket,
        "micromarket": token_micromarket,
    }


@pytest.fixture
def half_base():
    vegsupplier = User.objects.create(
        username="vegsupplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Иван",
        last_name="Иванов",
        company="Выборжец",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    grainsupplier = User.objects.create(
        username="grainsupplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Петр",
        last_name="Петров",
        company="Аладушкин",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    juice1supplier = User.objects.create(
        username="juice1supplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Николай",
        last_name="Николаев",
        company="Pepsico",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    juice2supplier = User.objects.create(
        username="juice2supplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Павел",
        last_name="Павлов",
        company="Мултон",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    breadsupplier = User.objects.create(
        username="breadsupplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Алексей",
        last_name="Алексеев",
        company="Каравай",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    admin = User.objects.create(
        username="admin",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Админ",
        last_name="Админов",
        company="Портал",
        position="админ",
        type="admin",
        is_superuser=True,
    )
    hypermarket = User.objects.create(
        username="hypermarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Ольга",
        last_name="Есенина",
        company="ОК",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )
    supermarket = User.objects.create(
        username="supermarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Ирина",
        last_name="Пушкина",
        company="5ка",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )
    minimarket = User.objects.create(
        username="minimarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Татьяна",
        last_name="Ахматова",
        company="Фасоль",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )
    micromarket = User.objects.create(
        username="micromarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Оксана",
        last_name="Фет",
        company="КиБ",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )

    token_vegsupplier = Token.objects.create(user=vegsupplier)
    token_grainsupplier = Token.objects.create(user=grainsupplier)
    token_juice1supplier = Token.objects.create(user=juice1supplier)
    token_juice2supplier = Token.objects.create(user=juice2supplier)
    token_breadsupplier = Token.objects.create(user=breadsupplier)
    token_admin = Token.objects.create(user=admin)
    token_hypermarket = Token.objects.create(user=hypermarket)
    token_supermarket = Token.objects.create(user=supermarket)
    token_minimarket = Token.objects.create(user=minimarket)
    token_micromarket = Token.objects.create(user=micromarket)

    supplier_vegsupplier = Supplier.objects.create(
        user=vegsupplier, name="Выборжец", address="Выборг", order_status=True
    )
    supplier_grainsupplier = Supplier.objects.create(
        user=grainsupplier,
        name="Аладушкин",
        address="Санкт-Петербург",
        order_status=False,
    )
    supplier_juice1supplier = Supplier.objects.create(
        user=juice1supplier,
        name="Pepsico",
        address="Санкт-Петербург",
        order_status=True,
    )
    supplier_juice2supplier = Supplier.objects.create(
        user=juice2supplier, name="Мултон", address="Санкт-Петербург", order_status=True
    )

    Purchaser.objects.create(user=hypermarket, name="ОК", address="Санкт-Петербург")
    Purchaser.objects.create(user=supermarket, name="5ка", address="Санкт-Петербург")
    Purchaser.objects.create(user=minimarket, name="Фасоль", address="Санкт-Петербург")

    vegetables = Category.objects.create(name="Овощи")
    grain = Category.objects.create(name="Крупа")
    juice = Category.objects.create(name="Сок")
    lemonade = Category.objects.create(name="Лимонад")
    water = Category.objects.create(name="Вода")

    tomato = Product.objects.create(name="Помидор", category=vegetables)
    cucumber = Product.objects.create(name="Огурец", category=vegetables)
    pepper = Product.objects.create(name="Перец", category=vegetables)
    rice = Product.objects.create(name="Рис", category=grain)
    buckwheat = Product.objects.create(name="Греча", category=grain)
    oat = Product.objects.create(name="Овсяная крупа", category=grain)
    orange_juice = Product.objects.create(name="Сок апельсиновый", category=juice)
    apple_juice = Product.objects.create(name="Сок яблочный", category=juice)
    tomato_juice = Product.objects.create(name="Сок томатный", category=juice)
    coca = Product.objects.create(name="Кока-кола", category=lemonade)
    pepsi = Product.objects.create(name="Пепси-кола", category=lemonade)
    fanta = Product.objects.create(name="Фанта", category=lemonade)
    mirinda = Product.objects.create(name="Миринда", category=lemonade)
    minerale = Product.objects.create(name="Aqua minerale", category=water)
    bonaqua = Product.objects.create(name="Bonaqua", category=water)

    tomato_stock = Stock.objects.create(
        product=tomato,
        supplier=supplier_vegsupplier,
        quantity=1000,
        price=150,
        price_rrc=200,
        sku="1234",
    )
    cucumber_stock = Stock.objects.create(
        product=cucumber,
        supplier=supplier_vegsupplier,
        quantity=2000,
        price=130,
        price_rrc=180,
        sku="9511",
    )
    pepper_stock = Stock.objects.create(
        product=pepper,
        supplier=supplier_vegsupplier,
        quantity=800,
        price=250,
        price_rrc=300,
        sku="5851",
    )
    rice_stock = Stock.objects.create(
        product=rice,
        supplier=supplier_grainsupplier,
        quantity=900,
        price=90,
        price_rrc=100,
        sku="2855",
    )
    buckwheat_stock = Stock.objects.create(
        product=buckwheat,
        supplier=supplier_grainsupplier,
        quantity=1000,
        price=120,
        price_rrc=150,
        sku="148465",
    )
    oat_stock = Stock.objects.create(
        product=oat,
        supplier=supplier_grainsupplier,
        quantity=1500,
        price=50,
        price_rrc=70,
        sku="65484",
    )
    orange1_stock = Stock.objects.create(
        product=orange_juice,
        supplier=supplier_juice1supplier,
        quantity=400,
        price=100,
        price_rrc=120,
        sku="5548",
    )
    orange2_stock = Stock.objects.create(
        product=orange_juice,
        supplier=supplier_juice2supplier,
        quantity=600,
        price=120,
        price_rrc=140,
        sku="4842",
    )
    apple1_stock = Stock.objects.create(
        product=apple_juice,
        supplier=supplier_juice1supplier,
        quantity=500,
        price=100,
        price_rrc=120,
        sku="7841",
    )
    apple2_stock = Stock.objects.create(
        product=apple_juice,
        supplier=supplier_juice2supplier,
        quantity=400,
        price=120,
        price_rrc=140,
        sku="0845",
    )
    tomato1_stock = Stock.objects.create(
        product=tomato_juice,
        supplier=supplier_juice1supplier,
        quantity=500,
        price=100,
        price_rrc=120,
        sku="99654",
    )
    tomato2_stock = Stock.objects.create(
        product=tomato_juice,
        supplier=supplier_juice2supplier,
        quantity=0,
        price=120,
        price_rrc=140,
        sku="8521",
    )
    coca_stock = Stock.objects.create(
        product=coca,
        supplier=supplier_juice2supplier,
        quantity=350,
        price=60,
        price_rrc=70,
        sku="79851",
    )
    pepsi_stock = Stock.objects.create(
        product=pepsi,
        supplier=supplier_juice1supplier,
        quantity=400,
        price=55,
        price_rrc=65,
        sku="698562",
    )
    fanta_stock = Stock.objects.create(
        product=fanta,
        supplier=supplier_juice2supplier,
        quantity=250,
        price=60,
        price_rrc=70,
        sku="5854",
    )
    mirinda_stock = Stock.objects.create(
        product=mirinda,
        supplier=supplier_juice1supplier,
        quantity=180,
        price=55,
        price_rrc=65,
        sku="4851",
    )
    minirale_stock = Stock.objects.create(
        product=minerale,
        supplier=supplier_juice1supplier,
        quantity=500,
        price=60,
        price_rrc=70,
        sku="2985",
    )
    bonaqua_stock = Stock.objects.create(
        product=bonaqua,
        supplier=supplier_juice2supplier,
        quantity=600,
        price=55,
        price_rrc=65,
        sku="285",
    )

    color = Characteristic.objects.create(name="Цвет")
    size = Characteristic.objects.create(name="Размер")
    weight = Characteristic.objects.create(name="Вес упаковки")
    volume = Characteristic.objects.create(name="Объем упаковки")
    mineralization = Characteristic.objects.create(name="Минерализация")

    ProductCharacteristic.objects.create(
        stock=tomato_stock, characteristic=color, value="Красный"
    )
    ProductCharacteristic.objects.create(
        stock=tomato_stock, characteristic=size, value="Желтый"
    )
    ProductCharacteristic.objects.create(
        stock=cucumber_stock, characteristic=color, value="Зеленый"
    )
    ProductCharacteristic.objects.create(
        stock=cucumber_stock, characteristic=size, value="Салатовый"
    )
    ProductCharacteristic.objects.create(
        stock=pepper_stock, characteristic=color, value="Красный"
    )
    ProductCharacteristic.objects.create(
        stock=pepper_stock, characteristic=size, value="Желтый"
    )
    ProductCharacteristic.objects.create(
        stock=rice_stock, characteristic=weight, value="900 гр"
    )
    ProductCharacteristic.objects.create(
        stock=buckwheat_stock, characteristic=weight, value="900 гр"
    )
    ProductCharacteristic.objects.create(
        stock=oat_stock, characteristic=weight, value="400 гр"
    )
    ProductCharacteristic.objects.create(
        stock=orange1_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=orange2_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=apple1_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=apple2_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=tomato1_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=tomato2_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=coca_stock, characteristic=volume, value="0.33 л"
    )
    ProductCharacteristic.objects.create(
        stock=pepsi_stock, characteristic=volume, value="0.33 л"
    )
    ProductCharacteristic.objects.create(
        stock=fanta_stock, characteristic=volume, value="0.33 л"
    )
    ProductCharacteristic.objects.create(
        stock=mirinda_stock, characteristic=volume, value="0.33 л"
    )
    ProductCharacteristic.objects.create(
        stock=minirale_stock, characteristic=volume, value="0.5 л"
    )
    ProductCharacteristic.objects.create(
        stock=minirale_stock,
        characteristic=mineralization,
        value="Высокоминерализованная",
    )
    ProductCharacteristic.objects.create(
        stock=bonaqua_stock, characteristic=volume, value="0.5 л"
    )
    ProductCharacteristic.objects.create(
        stock=bonaqua_stock,
        characteristic=mineralization,
        value="Низкоминерализованная",
    )

    return {
        "vegsupplier": token_vegsupplier,
        "grainsupplier": token_grainsupplier,
        "juice1supplier": token_juice1supplier,
        "juice2supplier": token_juice2supplier,
        "breadsupplier": token_breadsupplier,
        "admin": token_admin,
        "hypermarket": token_hypermarket,
        "supermarket": token_supermarket,
        "minimarket": token_minimarket,
        "micromarket": token_micromarket,
    }


@pytest.fixture
def full_base():
    vegsupplier = User.objects.create(
        username="vegsupplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Иван",
        last_name="Иванов",
        company="Выборжец",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    grainsupplier = User.objects.create(
        username="grainsupplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Петр",
        last_name="Петров",
        company="Аладушкин",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )

    juice1supplier = User.objects.create(
        username="juice1supplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Николай",
        last_name="Николаев",
        company="Pepsico",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    juice2supplier = User.objects.create(
        username="juice2supplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Павел",
        last_name="Павлов",
        company="Мултон",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    breadsupplier = User.objects.create(
        username="breadsupplier",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Алексей",
        last_name="Алексеев",
        company="Каравай",
        position="менеджер",
        type="supplier",
        is_superuser=False,
    )
    admin = User.objects.create(
        username="admin",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Админ",
        last_name="Админов",
        company="Портал",
        position="админ",
        type="admin",
        is_superuser=True,
    )
    hypermarket = User.objects.create(
        username="hypermarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Ольга",
        last_name="Есенина",
        company="ОК",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )
    supermarket = User.objects.create(
        username="supermarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Ирина",
        last_name="Пушкина",
        company="5ка",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )
    minimarket = User.objects.create(
        username="minimarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Татьяна",
        last_name="Ахматова",
        company="Фасоль",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )
    micromarket = User.objects.create(
        username="micromarket",
        email=TEST_EMAIL,
        password="Password1!",
        first_name="Оксана",
        last_name="Фет",
        company="КиБ",
        position="менеджер",
        type="purchaser",
        is_superuser=False,
    )

    token_vegsupplier = Token.objects.create(user=vegsupplier)
    token_grainsupplier = Token.objects.create(user=grainsupplier)

    token_juice1supplier = Token.objects.create(user=juice1supplier)
    token_juice2supplier = Token.objects.create(user=juice2supplier)
    token_breadsupplier = Token.objects.create(user=breadsupplier)
    token_admin = Token.objects.create(user=admin)
    token_hypermarket = Token.objects.create(user=hypermarket)
    token_supermarket = Token.objects.create(user=supermarket)
    token_minimarket = Token.objects.create(user=minimarket)
    token_micromarket = Token.objects.create(user=micromarket)

    supplier_vegsupplier = Supplier.objects.create(
        user=vegsupplier, name="Выборжец", address="Выборг", order_status=True
    )
    supplier_grainsupplier = Supplier.objects.create(
        user=grainsupplier,
        name="Аладушкин",
        address="Санкт-Петербург",
        order_status=False,
    )

    supplier_juice1supplier = Supplier.objects.create(
        user=juice1supplier,
        name="Pepsico",
        address="Санкт-Петербург",
        order_status=True,
    )
    supplier_juice2supplier = Supplier.objects.create(
        user=juice2supplier, name="Мултон", address="Санкт-Петербург", order_status=True
    )

    purchaser_hypermarket = Purchaser.objects.create(
        user=hypermarket, name="ОК", address="Санкт-Петербург"
    )
    purchaser_supermarket = Purchaser.objects.create(
        user=supermarket, name="5ка", address="Санкт-Петербург"
    )
    purchaser_minimarket = Purchaser.objects.create(
        user=minimarket, name="Фасоль", address="Санкт-Петербург"
    )

    vegetables = Category.objects.create(name="Овощи")
    grain = Category.objects.create(name="Крупа")
    juice = Category.objects.create(name="Сок")
    lemonade = Category.objects.create(name="Лимонад")
    water = Category.objects.create(name="Вода")

    tomato = Product.objects.create(name="Помидор", category=vegetables)
    cucumber = Product.objects.create(name="Огурец", category=vegetables)
    pepper = Product.objects.create(name="Перец", category=vegetables)
    rice = Product.objects.create(name="Рис", category=grain)
    buckwheat = Product.objects.create(name="Греча", category=grain)
    oat = Product.objects.create(name="Овсяная крупа", category=grain)
    orange_juice = Product.objects.create(name="Сок апельсиновый", category=juice)
    apple_juice = Product.objects.create(name="Сок яблочный", category=juice)
    tomato_juice = Product.objects.create(name="Сок томатный", category=juice)
    coca = Product.objects.create(name="Кока-кола", category=lemonade)
    pepsi = Product.objects.create(name="Пепси-кола", category=lemonade)
    fanta = Product.objects.create(name="Фанта", category=lemonade)
    mirinda = Product.objects.create(name="Миринда", category=lemonade)
    minerale = Product.objects.create(name="Aqua minerale", category=water)
    bonaqua = Product.objects.create(name="Bonaqua", category=water)

    tomato_stock = Stock.objects.create(
        product=tomato,
        supplier=supplier_vegsupplier,
        quantity=1000,
        price=150,
        price_rrc=200,
        sku="1234",
    )
    cucumber_stock = Stock.objects.create(
        product=cucumber,
        supplier=supplier_vegsupplier,
        quantity=2000,
        price=130,
        price_rrc=180,
        sku="9511",
    )
    pepper_stock = Stock.objects.create(
        product=pepper,
        supplier=supplier_vegsupplier,
        quantity=800,
        price=250,
        price_rrc=300,
        sku="5851",
    )
    rice_stock = Stock.objects.create(
        product=rice,
        supplier=supplier_grainsupplier,
        quantity=900,
        price=90,
        price_rrc=100,
        sku="2855",
    )
    buckwheat_stock = Stock.objects.create(
        product=buckwheat,
        supplier=supplier_grainsupplier,
        quantity=1000,
        price=120,
        price_rrc=150,
        sku="148465",
    )
    oat_stock = Stock.objects.create(
        product=oat,
        supplier=supplier_grainsupplier,
        quantity=1500,
        price=50,
        price_rrc=70,
        sku="65484",
    )
    orange1_stock = Stock.objects.create(
        product=orange_juice,
        supplier=supplier_juice1supplier,
        quantity=400,
        price=100,
        price_rrc=120,
        sku="5548",
    )
    orange2_stock = Stock.objects.create(
        product=orange_juice,
        supplier=supplier_juice2supplier,
        quantity=600,
        price=120,
        price_rrc=140,
        sku="4842",
    )
    apple1_stock = Stock.objects.create(
        product=apple_juice,
        supplier=supplier_juice1supplier,
        quantity=500,
        price=100,
        price_rrc=120,
        sku="7841",
    )
    apple2_stock = Stock.objects.create(
        product=apple_juice,
        supplier=supplier_juice2supplier,
        quantity=400,
        price=120,
        price_rrc=140,
        sku="0845",
    )
    tomato1_stock = Stock.objects.create(
        product=tomato_juice,
        supplier=supplier_juice1supplier,
        quantity=500,
        price=100,
        price_rrc=120,
        sku="99654",
    )
    tomato2_stock = Stock.objects.create(
        product=tomato_juice,
        supplier=supplier_juice2supplier,
        quantity=0,
        price=120,
        price_rrc=140,
        sku="8521",
    )
    coca_stock = Stock.objects.create(
        product=coca,
        supplier=supplier_juice2supplier,
        quantity=350,
        price=60,
        price_rrc=70,
        sku="79851",
    )
    pepsi_stock = Stock.objects.create(
        product=pepsi,
        supplier=supplier_juice1supplier,
        quantity=400,
        price=55,
        price_rrc=65,
        sku="698562",
    )
    fanta_stock = Stock.objects.create(
        product=fanta,
        supplier=supplier_juice2supplier,
        quantity=250,
        price=60,
        price_rrc=70,
        sku="5854",
    )
    mirinda_stock = Stock.objects.create(
        product=mirinda,
        supplier=supplier_juice1supplier,
        quantity=180,
        price=55,
        price_rrc=65,
        sku="4851",
    )
    minirale_stock = Stock.objects.create(
        product=minerale,
        supplier=supplier_juice1supplier,
        quantity=500,
        price=60,
        price_rrc=70,
        sku="2985",
    )
    bonaqua_stock = Stock.objects.create(
        product=bonaqua,
        supplier=supplier_juice2supplier,
        quantity=600,
        price=55,
        price_rrc=65,
        sku="285",
    )

    color = Characteristic.objects.create(name="Цвет")
    size = Characteristic.objects.create(name="Размер")
    weight = Characteristic.objects.create(name="Вес упаковки")
    volume = Characteristic.objects.create(name="Объем упаковки")
    mineralization = Characteristic.objects.create(name="Минерализация")

    ProductCharacteristic.objects.create(
        stock=tomato_stock, characteristic=color, value="Красный"
    )
    ProductCharacteristic.objects.create(
        stock=tomato_stock, characteristic=size, value="Желтый"
    )
    ProductCharacteristic.objects.create(
        stock=cucumber_stock, characteristic=color, value="Зеленый"
    )
    ProductCharacteristic.objects.create(
        stock=cucumber_stock, characteristic=size, value="Салатовый"
    )
    ProductCharacteristic.objects.create(
        stock=pepper_stock, characteristic=color, value="Красный"
    )
    ProductCharacteristic.objects.create(
        stock=pepper_stock, characteristic=size, value="Желтый"
    )
    ProductCharacteristic.objects.create(
        stock=rice_stock, characteristic=weight, value="900 гр"
    )
    ProductCharacteristic.objects.create(
        stock=buckwheat_stock, characteristic=weight, value="900 гр"
    )
    ProductCharacteristic.objects.create(
        stock=oat_stock, characteristic=weight, value="400 гр"
    )
    ProductCharacteristic.objects.create(
        stock=orange1_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=orange2_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=apple1_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=apple2_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=tomato1_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=tomato2_stock, characteristic=volume, value="1 л"
    )
    ProductCharacteristic.objects.create(
        stock=coca_stock, characteristic=volume, value="0.33 л"
    )
    ProductCharacteristic.objects.create(
        stock=pepsi_stock, characteristic=volume, value="0.33 л"
    )
    ProductCharacteristic.objects.create(
        stock=fanta_stock, characteristic=volume, value="0.33 л"
    )
    ProductCharacteristic.objects.create(
        stock=mirinda_stock, characteristic=volume, value="0.33 л"
    )
    ProductCharacteristic.objects.create(
        stock=minirale_stock, characteristic=volume, value="0.5 л"
    )
    ProductCharacteristic.objects.create(
        stock=minirale_stock,
        characteristic=mineralization,
        value="Высокоминерализованная",
    )
    ProductCharacteristic.objects.create(
        stock=bonaqua_stock, characteristic=volume, value="0.5 л"
    )
    ProductCharacteristic.objects.create(
        stock=bonaqua_stock,
        characteristic=mineralization,
        value="Низкоминерализованная",
    )

    german = ChainStore.objects.create(
        purchaser=purchaser_hypermarket,
        name="Германа",
        address="Германа",
        phone="89999999999",
    )
    zhukov = ChainStore.objects.create(
        purchaser=purchaser_hypermarket,
        name="Жукова",
        address="Жукова",
        phone="88888888888",
    )
    zanev = ChainStore.objects.create(
        purchaser=purchaser_hypermarket,
        name="Заневский",
        address="Заневский",
        phone="87777777777",
    )
    lenin = ChainStore.objects.create(
        purchaser=purchaser_supermarket,
        name="Ленинский",
        address="Ленинский",
        phone="86666666666",
    )

    ok_cart = ShoppingCart.objects.create(purchaser=purchaser_hypermarket)
    five_cart = ShoppingCart.objects.create(purchaser=purchaser_supermarket)
    ShoppingCart.objects.create(purchaser=purchaser_minimarket)

    CartPosition.objects.create(
        shopping_cart=ok_cart, stock=tomato_stock, quantity=100, price=150
    )
    CartPosition.objects.create(
        shopping_cart=ok_cart, stock=cucumber_stock, quantity=100, price=100
    )
    CartPosition.objects.create(
        shopping_cart=ok_cart, stock=pepper_stock, quantity=100, price=250
    )
    CartPosition.objects.create(
        shopping_cart=five_cart, stock=tomato_stock, quantity=100, price=150
    )
    CartPosition.objects.create(
        shopping_cart=five_cart, stock=buckwheat_stock, quantity=100, price=120
    )
    CartPosition.objects.create(
        shopping_cart=five_cart, stock=orange1_stock, quantity=50, price=100
    )
    CartPosition.objects.create(
        shopping_cart=five_cart, stock=fanta_stock, quantity=70, price=60
    )

    order1_ok = Order.objects.create(
        purchaser=purchaser_hypermarket, chain_store=german
    )
    order2_ok = Order.objects.create(
        purchaser=purchaser_hypermarket, chain_store=zhukov
    )
    order3_ok = Order.objects.create(
        purchaser=purchaser_hypermarket, chain_store=zanev, status="cancelled"
    )
    order1_5 = Order.objects.create(purchaser=purchaser_supermarket, chain_store=lenin)
    order2_5 = Order.objects.create(purchaser=purchaser_supermarket, chain_store=lenin)
    order3_5 = Order.objects.create(purchaser=purchaser_supermarket, chain_store=lenin)
    order4_5 = Order.objects.create(
        purchaser=purchaser_supermarket, chain_store=lenin, status="cancelled"
    )

    OrderPosition.objects.create(
        order=order1_ok, stock=orange1_stock, quantity=100, price=100
    )
    OrderPosition.objects.create(
        order=order1_ok, stock=orange2_stock, quantity=100, price=120
    )
    OrderPosition.objects.create(
        order=order1_ok, stock=apple1_stock, quantity=100, price=100
    )
    OrderPosition.objects.create(
        order=order1_ok, stock=apple2_stock, quantity=100, price=120
    )
    OrderPosition.objects.create(
        order=order1_ok, stock=tomato1_stock, quantity=100, price=100
    )
    OrderPosition.objects.create(
        order=order1_ok, stock=tomato2_stock, quantity=100, price=120
    )

    OrderPosition.objects.create(
        order=order2_ok, stock=tomato_stock, quantity=1000, price=150, confirmed=True
    )
    OrderPosition.objects.create(
        order=order2_ok, stock=cucumber_stock, quantity=1000, price=130, confirmed=True
    )
    OrderPosition.objects.create(
        order=order2_ok, stock=pepper_stock, quantity=1000, price=250, confirmed=True
    )

    OrderPosition.objects.create(
        order=order3_ok, stock=rice_stock, quantity=1000, price=90
    )

    OrderPosition.objects.create(
        order=order1_5,
        stock=orange1_stock,
        quantity=500,
        price=100,
        confirmed=True,
        delivered=True,
    )
    OrderPosition.objects.create(
        order=order1_5, stock=orange2_stock, quantity=500, price=120, confirmed=True
    )

    OrderPosition.objects.create(
        order=order2_5, stock=tomato_stock, quantity=200, price=150, confirmed=True
    )
    OrderPosition.objects.create(
        order=order2_5, stock=cucumber_stock, quantity=200, price=130, confirmed=True
    )
    OrderPosition.objects.create(
        order=order2_5, stock=pepper_stock, quantity=200, price=250, confirmed=True
    )
    OrderPosition.objects.create(
        order=order2_5, stock=minirale_stock, quantity=100, price=60
    )

    OrderPosition.objects.create(
        order=order3_5,
        stock=coca_stock,
        quantity=100,
        price=60,
        confirmed=True,
        delivered=True,
    )
    OrderPosition.objects.create(
        order=order3_5,
        stock=fanta_stock,
        quantity=100,
        price=60,
        confirmed=True,
        delivered=True,
    )

    OrderPosition.objects.create(
        order=order4_5, stock=bonaqua_stock, quantity=500, price=55
    )

    return {
        "vegsupplier": token_vegsupplier,
        "grainsupplier": token_grainsupplier,
        "juice1supplier": token_juice1supplier,
        "juice2supplier": token_juice2supplier,
        "breadsupplier": token_breadsupplier,
        "admin": token_admin,
        "hypermarket": token_hypermarket,
        "supermarket": token_supermarket,
        "minimarket": token_minimarket,
        "micromarket": token_micromarket,
    }
