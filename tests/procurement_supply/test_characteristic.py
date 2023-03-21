import pytest

from procurement_supply.models import Characteristic, ProductCharacteristic


@pytest.mark.django_db
def test_create_characteristic_no_token(client, half_base):
    data = {"name": "Вкус"}
    response = client.post("/api/v1/characteristics/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_create_characteristic_wrong_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    data = {"name": "Вкус"}
    response = client.post("/api/v1/characteristics/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_create_characteristic_admin(client, half_base):
    count = Characteristic.objects.count()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    data = {"name": "Вкус"}
    response = client.post("/api/v1/characteristics/", data=data, format="json")
    assert response.status_code == 201
    assert Characteristic.objects.count() == count + 1
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_create_characteristic_purchaser_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    data = {"name": "Вкус"}
    response = client.post("/api/v1/characteristics/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_characteristic_supplier_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {"name": "Вкус"}
    response = client.post("/api/v1/characteristics/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_create_characteristic_no_name(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.post("/api/v1/characteristics/", format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"name": ["This field is required."]}


@pytest.mark.django_db
def test_create_characteristic_exists(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {"name": "Цвет"}
    response = client.post("/api/v1/characteristics/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"name": ["Характеристика with this name already exists."]}


@pytest.mark.django_db
def test_list_characteristic_no_token(client, half_base):
    response = client.get("/api/v1/characteristics/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_characteristic_wrong_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.get("/api/v1/characteristics/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.parametrize(["token"], (("minimarket",), ("vegsupplier",), ("admin",)))
@pytest.mark.django_db
def test_list_characteristic_token(client, half_base, token):
    client.credentials(HTTP_AUTHORIZATION=f"Token {half_base[token]}")
    response = client.get("/api/v1/characteristics/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 5


@pytest.mark.django_db
def test_retrieve_characteristic_no_token(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    response = client.get(f"/api/v1/characteristics/{color.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_characteristic_wrong_token(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.get(f"/api/v1/characteristics/{color.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.parametrize(["token"], (("minimarket",), ("vegsupplier",), ("admin",)))
@pytest.mark.django_db
def test_retrieve_characteristic_token(client, half_base, token):
    color = Characteristic.objects.get(name="Цвет")
    client.credentials(HTTP_AUTHORIZATION=f"Token {half_base[token]}")
    response = client.get(f"/api/v1/characteristics/{color.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == "Цвет"


@pytest.mark.django_db
def test_destroy_characteristic_no_token(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    response = client.delete(f"/api/v1/characteristics/{color.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_destroy_characteristic_wrong_token(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    response = client.delete(f"/api/v1/characteristics/{color.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_destroy_characteristic_admin_token(client, half_base):
    count_char = Characteristic.objects.count()
    count_stock_char = ProductCharacteristic.objects.count()
    color = Characteristic.objects.get(name="Цвет")
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.delete(f"/api/v1/characteristics/{color.id}/", format="json")
    assert response.status_code == 204
    assert Characteristic.objects.count() == count_char - 1
    assert ProductCharacteristic.objects.count() == count_stock_char - 3


@pytest.mark.django_db
def test_destroy_characteristic_purchaser_token(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.delete(f"/api/v1/characteristics/{color.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_characteristic_supplier_token(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.delete(f"/api/v1/characteristics/{color.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_characteristic_no_token(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    data = {"name": "Color"}
    response = client.patch(
        f"/api/v1/characteristics/{color.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_characteristic_wrong_token(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    data = {"name": "Color"}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    response = client.patch(
        f"/api/v1/characteristics/{color.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_update_characteristic_purchaser_token(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    data = {"name": "Color"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.patch(
        f"/api/v1/characteristics/{color.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_characteristics_supplier_token(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    data = {"name": "Color"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/characteristics/{color.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_characteristic_admin_token(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    data = {"name": "Color"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.patch(
        f"/api/v1/characteristics/{color.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_update_characteristic_exists(client, half_base):
    color = Characteristic.objects.get(name="Цвет")
    data = {"name": "Размер"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.patch(
        f"/api/v1/characteristics/{color.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"name": ["Характеристика with this name already exists."]}
