import pytest

from procurement_supply.models import (Category, Characteristic, Product,
                                       ProductCharacteristic, Stock, Supplier)


# @pytest.mark.django_db
# def test_import_user_category_exists(client, half_base):
#     if not Category.objects.filter(id=1).exists():
#         Category.objects.create(id=1, name="test")
#     data = {
#         "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
#     }
#     client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["breadsupplier"]}')
#     response = client.post("/api/v1/import/", data=data, format="json")
#     assert response.status_code == 400
#     reply = response.json()
#     assert reply == {
#         "error": "Category with id from your file already exists with another name"
#     }


@pytest.mark.django_db
def test_import_no_token(client, half_base):
    data = {
        "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
    }
    response = client.post("/api/v1/import/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_import_wrong_token(client, half_base):
    data = {
        "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
    }
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["breadsupplier"]}')
    response = client.post("/api/v1/import/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_import_admin_token(client, half_base):
    data = {
        "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
    }
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.post("/api/v1/import/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_import_purchaser_token(client, half_base):
    data = {
        "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
    }
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.post("/api/v1/import/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


# @pytest.mark.django_db
# def test_import_url_invalid(client, half_base):
#     data = {"url": "url"}
#     client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["breadsupplier"]}')
#     response = client.post("/api/v1/import/", data=data, format="json")
#     assert response.status_code == 400
#     reply = response.json()
#     assert reply == {"error": ["Enter a valid URL."]}


@pytest.mark.django_db
def test_import_no_url(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["breadsupplier"]}')
    response = client.post("/api/v1/import/", format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"url": ["This field is required."]}


# @pytest.mark.django_db
# def test_import_user_has_another_supplier(client, half_base):
#     data = {
#         "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
#     }
#     client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
#     response = client.post("/api/v1/import/", data=data, format="json")
#     assert response.status_code == 400
#     reply = response.json()
#     assert reply == {
#         "error": "Request user already refers to another supplier instance"
#     }


# @pytest.mark.django_db
# def test_import_user_success(client, half_base):
#     if Category.objects.filter(id=1).exists():
#         Category.objects.get(id=1).delete()
#     count_supplier = Supplier.objects.count()
#     count_category = Category.objects.count()
#     count_product = Product.objects.count()
#     count_stock = Stock.objects.count()
#     count_characteristic = Characteristic.objects.count()
#     count_product_characteristic = ProductCharacteristic.objects.count()
#     data = {
#         "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
#     }
#     client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["breadsupplier"]}')
#     response = client.post("/api/v1/import/", data=data, format="json")
#     assert response.status_code == 201
#     reply = response.json()
#     assert reply == {"success": "Import or update performed successfully"}
#     assert Supplier.objects.count() == count_supplier + 1
#     assert Category.objects.count() == count_category + 3
#     assert Product.objects.count() == count_product + 4
#     assert Stock.objects.count() == count_stock + 4
#     assert Characteristic.objects.count() == count_characteristic + 3
#     assert ProductCharacteristic.objects.count() == count_product_characteristic + 16


# @pytest.mark.django_db
# def test_update_absent_stock_nulled(client, half_base):
#     if Category.objects.filter(id=1).exists():
#         Category.objects.get(id=1).delete()
#
#     data = {
#         "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
#     }
#     client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["breadsupplier"]}')
#     client.post("/api/v1/import/", data=data, format="json")
#
#     product = Product.objects.filter(name="Рис").first()
#     supplier = Supplier.objects.filter(name="Связной").first()
#     rice = Stock.objects.create(
#         product=product,
#         supplier=supplier,
#         sku="Рис",
#         quantity=100,
#         price=100,
#         price_rrc=100,
#     )
#
#     data = {
#         "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
#     }
#     client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["breadsupplier"]}')
#     client.post("/api/v1/import/", data=data, format="json")
#
#     assert Stock.objects.get(id=rice.id).quantity == 0
