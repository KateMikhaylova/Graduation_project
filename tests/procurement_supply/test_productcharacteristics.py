import pytest

from procurement_supply.models import (Characteristic, ProductCharacteristic, Stock)


@pytest.mark.django_db
def test_create_product_characteristic_no_token(client, half_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    characteristic = Characteristic.objects.filter(name="Вес упаковки").first()
    data = {"stock": stock.id, "characteristic": characteristic.id, "value": "500 г"}
    response = client.post("/api/v1/product_characteristics/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_create_product_characteristic_wrong_token(client, half_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    characteristic = Characteristic.objects.filter(name="Вес упаковки").first()
    data = {"stock": stock.id, "characteristic": characteristic.id, "value": "500 г"}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.post("/api/v1/product_characteristics/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_create_product_characteristic_admin_token(client, half_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    characteristic = Characteristic.objects.filter(name="Вес упаковки").first()
    data = {"stock": stock.id, "characteristic": characteristic.id, "value": "500 г"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.post("/api/v1/product_characteristics/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_product_characteristic_purchaser_token(client, half_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    characteristic = Characteristic.objects.filter(name="Вес упаковки").first()
    data = {"stock": stock.id, "characteristic": characteristic.id, "value": "500 г"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.post("/api/v1/product_characteristics/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_product_characteristic_other_supplier_token(client, half_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    characteristic = Characteristic.objects.filter(name="Вес упаковки").first()
    data = {"stock": stock.id, "characteristic": characteristic.id, "value": "500 г"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["grainsupplier"]}')
    response = client.post("/api/v1/product_characteristics/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_product_characteristic_supplier_token(client, half_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    characteristic = Characteristic.objects.filter(name="Вес упаковки").first()
    data = {"stock": stock.id, "characteristic": characteristic.id, "value": "500 г"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.post("/api/v1/product_characteristics/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["value"] == data["value"]


@pytest.mark.django_db
def test_create_product_characteristic_no_stock(client, half_base):
    characteristic = Characteristic.objects.filter(name="Вес упаковки").first()
    data = {"characteristic": characteristic.id, "value": "500 г"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.post("/api/v1/product_characteristics/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "error": '"stock" is either not indicated or such stock does not exist'
    }


@pytest.mark.django_db
def test_create_product_characteristic_odd_stock(client, half_base):
    characteristic = Characteristic.objects.filter(name="Вес упаковки").first()
    data = {"stock": 999999999, "characteristic": characteristic.id, "value": "500 г"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.post("/api/v1/product_characteristics/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "error": '"stock" is either not indicated or such stock does not exist'
    }


@pytest.mark.django_db
def test_create_product_characteristic_no_char(client, half_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id, "value": "500 г"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.post("/api/v1/product_characteristics/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"characteristic": ["This field is required."]}


@pytest.mark.django_db
def test_create_product_characteristic_no_value(client, half_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    characteristic = Characteristic.objects.filter(name="Вес упаковки").first()
    data = {"stock": stock.id, "characteristic": characteristic.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.post("/api/v1/product_characteristics/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"value": ["This field is required."]}


@pytest.mark.django_db
def test_create_product_characteristic_exists(client, half_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    characteristic = Characteristic.objects.filter(name="Цвет").first()
    data = {"stock": stock.id, "characteristic": characteristic.id, "value": "Зеленый"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.post("/api/v1/product_characteristics/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "this stock already has this characteristic"}


@pytest.mark.django_db
def test_list_product_characteristic_no_token(client, half_base):
    response = client.get("/api/v1/product_characteristics/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_product_characteristic_wrong_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.get("/api/v1/product_characteristics/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.parametrize(["token"], (("minimarket",), ("vegsupplier",), ("admin",)))
@pytest.mark.django_db
def test_list_product_characteristic_tokens(client, half_base, token):
    client.credentials(HTTP_AUTHORIZATION=f"Token {half_base[token]}")
    response = client.get("/api/v1/product_characteristics/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 23


@pytest.mark.django_db
def test_retrieve_product_characteristic_no_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    response = client.get(f"/api/v1/product_characteristics/{char.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_product_characteristic_wrong_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.get(f"/api/v1/product_characteristics/{char.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.parametrize(["token"], (("minimarket",), ("vegsupplier",), ("admin",)))
@pytest.mark.django_db
def test_retrieve_product_characteristic_tokens(client, half_base, token):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    client.credentials(HTTP_AUTHORIZATION=f"Token {half_base[token]}")
    response = client.get(f"/api/v1/product_characteristics/{char.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["value"] == "Зеленый"


@pytest.mark.django_db
def test_destroy_product_characteristic_no_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    response = client.delete(
        f"/api/v1/product_characteristics/{char.id}/", format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_destroy_product_characteristic_wrong_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.delete(
        f"/api/v1/product_characteristics/{char.id}/", format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_destroy_product_characteristic_admin_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.delete(
        f"/api/v1/product_characteristics/{char.id}/", format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_product_characteristic_purchaser_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.delete(
        f"/api/v1/product_characteristics/{char.id}/", format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_product_characteristic_other_supplier_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["grainsupplier"]}')
    response = client.delete(
        f"/api/v1/product_characteristics/{char.id}/", format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_product_characteristic_supplier_token(client, half_base):
    count = ProductCharacteristic.objects.count()
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.delete(
        f"/api/v1/product_characteristics/{char.id}/", format="json"
    )
    assert response.status_code == 204
    assert ProductCharacteristic.objects.count() == count - 1


@pytest.mark.django_db
def test_update_product_characteristic_no_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    data = {"value": "Желтый"}
    response = client.patch(
        f"/api/v1/product_characteristics/{char.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_product_characteristic_wrong_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    data = {"value": "Желтый"}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/product_characteristics/{char.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_update_product_characteristic_admin_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    data = {"value": "Желтый"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.patch(
        f"/api/v1/product_characteristics/{char.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_product_characteristic_purchaser_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    data = {"value": "Желтый"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.patch(
        f"/api/v1/product_characteristics/{char.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_product_characteristic_other_supplier_token(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    data = {"value": "Желтый"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["grainsupplier"]}')
    response = client.patch(
        f"/api/v1/product_characteristics/{char.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_product_characteristic_success(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    data = {"value": "Желтый"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/product_characteristics/{char.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["value"] == data["value"]


@pytest.mark.django_db
def test_update_product_characteristic_stock(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    data = {"stock": 1}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/product_characteristics/{char.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": 'Only "value" field can be amended'}


@pytest.mark.django_db
def test_update_product_characteristic_characteristic(client, half_base):
    char = ProductCharacteristic.objects.filter(value="Зеленый").first()
    data = {"characteristic": 2}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/product_characteristics/{char.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": 'Only "value" field can be amended'}
