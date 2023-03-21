import pytest

from procurement_supply.models import (Category, Product,
                                       ProductCharacteristic, Stock)


@pytest.mark.django_db
def test_create_product_no_token(client, half_base):
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Морковь", "category": veg.id}
    response = client.post("/api/v1/products/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_create_product_wrong_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Морковь", "category": veg.id}
    response = client.post("/api/v1/products/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_create_product_admin(client, half_base):
    count = Product.objects.count()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Морковь", "category": veg.id}
    response = client.post("/api/v1/products/", data=data, format="json")
    assert response.status_code == 201
    assert Product.objects.count() == count + 1
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_create_product_purchaser_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Морковь", "category": veg.id}
    response = client.post("/api/v1/products/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_product_supplier_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Морковь", "category": veg.id}
    response = client.post("/api/v1/products/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_create_product_no_name(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    veg = Category.objects.get(name="Овощи")
    data = {"category": veg.id}
    response = client.post("/api/v1/products/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"name": ["This field is required."]}


@pytest.mark.django_db
def test_create_product_no_category(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {"name": "Морковь"}
    response = client.post("/api/v1/products/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"category": ["This field is required."]}


@pytest.mark.django_db
def test_create_product_exists(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    veg = Category.objects.get(name="Овощи")
    data = {"name": "Перец", "category": veg.id}
    response = client.post("/api/v1/products/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_list_product_no_token(client, half_base):
    response = client.get("/api/v1/products/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_product_wrong_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.get("/api/v1/products/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.parametrize(["token"], (("minimarket",), ("vegsupplier",), ("admin",)))
@pytest.mark.django_db
def test_list_product_token(client, half_base, token):
    client.credentials(HTTP_AUTHORIZATION=f"Token {half_base[token]}")
    response = client.get("/api/v1/products/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 15


@pytest.mark.django_db
def test_retrieve_product_no_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    response = client.get(f"/api/v1/products/{cucumber.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_product_wrong_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.get(f"/api/v1/products/{cucumber.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.parametrize(["token"], (("minimarket",), ("vegsupplier",), ("admin",)))
@pytest.mark.django_db
def test_retrieve_product_token(client, half_base, token):
    cucumber = Product.objects.filter(name="Огурец").first()
    client.credentials(HTTP_AUTHORIZATION=f"Token {half_base[token]}")
    response = client.get(f"/api/v1/products/{cucumber.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == "Огурец"


@pytest.mark.django_db
def test_destroy_product_no_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    response = client.delete(f"/api/v1/products/{cucumber.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_destroy_product_wrong_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    response = client.delete(f"/api/v1/products/{cucumber.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_destroy_product_admin_token(client, half_base):
    count_product = Product.objects.count()
    count_stock = Stock.objects.count()
    count_char = ProductCharacteristic.objects.count()
    cucumber = Product.objects.filter(name="Огурец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.delete(f"/api/v1/products/{cucumber.id}/", format="json")
    assert response.status_code == 204
    assert Product.objects.count() == count_product - 1
    assert Stock.objects.count() == count_stock - 1
    assert ProductCharacteristic.objects.count() == count_char - 2


@pytest.mark.django_db
def test_destroy_product_purchaser_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.delete(f"/api/v1/products/{cucumber.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_product_supplier_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.delete(f"/api/v1/products/{cucumber.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_product_no_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    data = {"name": "Огурцы"}
    response = client.patch(
        f"/api/v1/products/{cucumber.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_product_wrong_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    data = {"name": "Огурцы"}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    response = client.patch(
        f"/api/v1/products/{cucumber.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_update_product_purchaser_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    data = {"name": "Огурцы"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.patch(
        f"/api/v1/products/{cucumber.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_product_supplier_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    data = {"name": "Огурцы"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/products/{cucumber.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_product_name_admin_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    data = {"name": "Огурцы"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.patch(
        f"/api/v1/products/{cucumber.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_update_product_category_admin_token(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    category = Category.objects.get(name="Сок")
    data = {"category": category.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.patch(
        f"/api/v1/products/{cucumber.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["category"] == category.id


@pytest.mark.django_db
def test_update_product_exists(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    data = {"name": "Помидор"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.patch(
        f"/api/v1/products/{cucumber.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_get_product_filter_id(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.get(f"/api/v1/products/?id={cucumber.id}", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 1
    assert reply["results"][0]["name"] == cucumber.name


@pytest.mark.django_db
def test_get_product_filter_name(client, half_base):
    cucumber = Product.objects.filter(name="Огурец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.get(f"/api/v1/products/?name={cucumber.name}", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 1
    assert reply["results"][0]["id"] == cucumber.id


@pytest.mark.django_db
def test_get_product_filter_category_id(client, half_base):
    veg = Category.objects.get(name="Овощи")
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.get(f"/api/v1/products/?category__id={veg.id}", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 3
    assert reply["results"][0]["name"] == "Огурец"
    assert reply["results"][1]["name"] == "Перец"
    assert reply["results"][2]["name"] == "Помидор"


@pytest.mark.django_db
def test_get_product_filter_category_name(client, half_base):
    lemonade = Category.objects.get(name="Лимонад")
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.get(
        f"/api/v1/products/?category__name={lemonade.name}", format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 4


@pytest.mark.django_db
def test_get_product_search_name(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.get(f"/api/v1/products/?search=кола", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 2
    assert reply["results"][0]["name"] == "Кока-кола"
    assert reply["results"][1]["name"] == "Пепси-кола"
