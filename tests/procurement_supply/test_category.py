import pytest

from procurement_supply.models import (Category, Product,
                                       ProductCharacteristic, Stock)


@pytest.mark.django_db
def test_create_category_no_token(client, half_base):
    data = {"name": "Фрукты"}
    response = client.post("/api/v1/categories/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_create_category_wrong_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    data = {"name": "Фрукты"}
    response = client.post("/api/v1/categories/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_create_category_admin(client, half_base):
    count = Category.objects.count()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    data = {"name": "Фрукты"}
    response = client.post("/api/v1/categories/", data=data, format="json")
    assert response.status_code == 201
    assert Category.objects.count() == count + 1
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_create_category_purchaser_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    data = {"name": "Фрукты"}
    response = client.post("/api/v1/categories/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_category_supplier_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {"name": "Фрукты"}
    response = client.post("/api/v1/categories/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_create_category_no_name(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.post("/api/v1/categories/", format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"name": ["This field is required."]}


@pytest.mark.django_db
def test_create_category_exists(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {"name": "Овощи"}
    response = client.post("/api/v1/categories/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"name": ["Категория with this name already exists."]}


@pytest.mark.django_db
def test_list_category_no_token(client, half_base):
    response = client.get("/api/v1/categories/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_category_wrong_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.get("/api/v1/categories/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.parametrize(["token"], (("minimarket",), ("vegsupplier",), ("admin",)))
@pytest.mark.django_db
def test_list_category_token(client, half_base, token):
    client.credentials(HTTP_AUTHORIZATION=f"Token {half_base[token]}")
    response = client.get("/api/v1/categories/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 5


@pytest.mark.django_db
def test_retrieve_category_no_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    response = client.get(f"/api/v1/categories/{veg.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_category_wrong_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.get(f"/api/v1/categories/{veg.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.parametrize(["token"], (("minimarket",), ("vegsupplier",), ("admin",)))
@pytest.mark.django_db
def test_retrieve_category_token(client, half_base, token):
    veg = Category.objects.get(name="Овощи")
    client.credentials(HTTP_AUTHORIZATION=f"Token {half_base[token]}")
    response = client.get(f"/api/v1/categories/{veg.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == "Овощи"


@pytest.mark.django_db
def test_destroy_category_no_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    response = client.delete(f"/api/v1/categories/{veg.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_destroy_category_wrong_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    response = client.delete(f"/api/v1/categories/{veg.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_destroy_category_admin_token(client, half_base):
    count_category = Category.objects.count()
    count_product = Product.objects.count()
    count_stock = Stock.objects.count()
    count_char = ProductCharacteristic.objects.count()
    veg = Category.objects.get(name="Овощи")
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.delete(f"/api/v1/categories/{veg.id}/", format="json")
    assert response.status_code == 204
    assert Category.objects.count() == count_category - 1
    assert Product.objects.count() == count_product - 3
    assert Stock.objects.count() == count_stock - 3
    assert ProductCharacteristic.objects.count() == count_char - 6


@pytest.mark.django_db
def test_destroy_category_purchaser_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.delete(f"/api/v1/categories/{veg.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_category_supplier_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.delete(f"/api/v1/categories/{veg.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_category_no_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Овощ"}
    response = client.patch(f"/api/v1/categories/{veg.id}/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_category_wrong_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Овощ"}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    response = client.patch(f"/api/v1/categories/{veg.id}/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_update_category_purchaser_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Овощ"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.patch(f"/api/v1/categories/{veg.id}/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_category_supplier_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Овощ"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(f"/api/v1/categories/{veg.id}/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_category_admin_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Овощ"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.patch(f"/api/v1/categories/{veg.id}/", data=data, format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_update_category_exists(client, half_base):
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Вода"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.patch(f"/api/v1/categories/{veg.id}/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"name": ["Категория with this name already exists."]}


@pytest.mark.django_db
def test_get_category_filter_id(client, half_base):
    veg = Category.objects.get(name="Овощи")
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.get(f"/api/v1/categories/?id={veg.id}", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 1
    assert reply["results"][0]["name"] == veg.name


@pytest.mark.django_db
def test_get_category_filter_name(client, half_base):
    veg = Category.objects.get(name="Овощи")
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.get(f"/api/v1/categories/?name={veg.name}", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 1
    assert reply["results"][0]["id"] == veg.id


@pytest.mark.django_db
def test_get_category_search_name(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.get(f"/api/v1/categories/?search=д", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 2
    assert reply["results"][0]["name"] == "Вода"
    assert reply["results"][1]["name"] == "Лимонад"
