import pytest

from procurement_supply.models import (Product, ProductCharacteristic, Stock,
                                       Supplier)


@pytest.mark.django_db
def test_create_stock_no_token(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    data = {
        "product": product.id,
        "sku": "another articul",
        "quantity": 100,
        "price": 100,
        "price_rrc": 100,
    }
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_create_stock_wrong_token(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    data = {
        "product": product.id,
        "sku": "another articul",
        "quantity": 100,
        "price": 100,
        "price_rrc": 100,
    }
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_create_stock_admin_token(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    data = {
        "product": product.id,
        "sku": "another articul",
        "quantity": 100,
        "price": 100,
        "price_rrc": 100,
    }
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_stock_purchaser_token(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    data = {
        "product": product.id,
        "sku": "another articul",
        "quantity": 100,
        "price": 100,
        "price_rrc": 100,
    }
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_stock_supplier_token(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {
        "product": product.id,
        "sku": "another articul",
        "quantity": 100,
        "price": 100,
        "price_rrc": 100,
    }
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["product"] == product.id
    assert reply["supplier"] == Supplier.objects.filter(name="Выборжец").first().id
    assert reply["quantity"] == data["quantity"]
    assert reply["product_characteristics"] == []


@pytest.mark.django_db
def test_create_stock_supplier_no_instance_token(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["breadsupplier"]}')
    data = {
        "product": product.id,
        "sku": "another articul",
        "quantity": 100,
        "price": 100,
        "price_rrc": 100,
    }
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "error": "you need to create Supplier before you create or update Stock"
    }


@pytest.mark.django_db
def test_create_stock_supplier_put_another_supplier(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    another = Supplier.objects.filter(name="Аладушкин").first()
    data = {
        "supplier": another.id,
        "product": product.id,
        "sku": "another articul",
        "quantity": 100,
        "price": 100,
        "price_rrc": 100,
    }
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["supplier"] == Supplier.objects.filter(name="Выборжец").first().id


@pytest.mark.django_db
def test_create_stock_exists(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {
        "product": product.id,
        "quantity": 100,
        "price": 100,
        "price_rrc": 100,
        "sku": "1234",
    }
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "This Stock already exists"}


@pytest.mark.django_db
def test_create_stock_no_sku(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {"product": product.id, "quantity": 100, "price": 100, "price_rrc": 100}
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"sku": ["This field is required."]}


@pytest.mark.django_db
def test_create_stock_no_price_rrc(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {"product": product.id, "quantity": 100, "price": 100, "sku": "59873218"}
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"price_rrc": ["This field is required."]}


@pytest.mark.django_db
def test_create_stock_no_price(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {"product": product.id, "quantity": 100, "price_rrc": 100, "sku": "59873218"}
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"price": ["This field is required."]}


@pytest.mark.django_db
def test_create_stock_no_quantity(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {"product": product.id, "price": 100, "price_rrc": 100, "sku": "59873218"}
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"quantity": ["This field is required."]}


@pytest.mark.django_db
def test_create_stock_no_product(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {"quantity": 100, "price": 100, "price_rrc": 100, "sku": "59873218"}
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"product": ["This field is required."]}


@pytest.mark.django_db
def test_create_stock_odd_quantity(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {
        "product": product.id,
        "sku": "another articul",
        "quantity": -1,
        "price": 100,
        "price_rrc": 100,
    }
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"quantity": ["Ensure this value is greater than or equal to 0."]}


@pytest.mark.django_db
def test_create_stock_odd_price(client, half_base):
    product = Product.objects.filter(name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {
        "product": product.id,
        "sku": "another articul",
        "quantity": 2,
        "price": 0,
        "price_rrc": 100,
    }
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"price": ["Ensure this value is greater than or equal to 0.01."]}


@pytest.mark.django_db
def test_create_stock_product_does_not_exist(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    data = {
        "product": 99999999,
        "sku": "another articul",
        "quantity": 2,
        "price": 10,
        "price_rrc": 100,
    }
    response = client.post("/api/v1/stocks/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"product": ['Invalid pk "99999999" - object does not exist.']}


@pytest.mark.django_db
def test_list_stock_no_token(client, half_base):
    response = client.get("/api/v1/stocks/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_stock_wrong_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    response = client.get("/api/v1/stocks/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_list_stock_admin_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.get("/api/v1/stocks/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 18


@pytest.mark.django_db
def test_list_stock_supplier_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["juice1supplier"]}')
    response = client.get("/api/v1/stocks/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 6


@pytest.mark.django_db
def test_list_stock_purchaser_token(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.get("/api/v1/stocks/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 14


@pytest.mark.django_db
def test_retrieve_stock_no_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    response = client.get(f"/api/v1/stocks/{tomato.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_stock_wrong_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    response = client.get(f"/api/v1/stocks/{tomato.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_retrieve_stock_admin_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.get(f"/api/v1/stocks/{tomato.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["product"] == tomato.product.id
    assert reply["id"] == tomato.id
    assert reply["supplier"] == tomato.supplier.id


@pytest.mark.django_db
def test_retrieve_stock_purchaser_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.get(f"/api/v1/stocks/{tomato.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["product"] == tomato.product.id
    assert reply["id"] == tomato.id
    assert reply["supplier"] == tomato.supplier.id


@pytest.mark.django_db
def test_retrieve_stock_owner_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.get(f"/api/v1/stocks/{tomato.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["product"] == tomato.product.id
    assert reply["id"] == tomato.id
    assert reply["supplier"] == tomato.supplier.id


@pytest.mark.django_db
def test_retrieve_stock_other_supplier_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["breadsupplier"]}')
    response = client.get(f"/api/v1/stocks/{tomato.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_delete_stock_no_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    response = client.delete(f"/api/v1/stocks/{tomato.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_delete_stock_wrong_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["admin"]}')
    response = client.delete(f"/api/v1/stocks/{tomato.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_delete_stock_purchaser_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.delete(f"/api/v1/stocks/{tomato.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_delete_stock_supplier_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.delete(f"/api/v1/stocks/{tomato.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_delete_stock_admin_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    count_stock = Stock.objects.count()
    count_char = ProductCharacteristic.objects.count()
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.delete(f"/api/v1/stocks/{tomato.id}/", format="json")
    assert response.status_code == 204
    assert Stock.objects.count() == count_stock - 1
    assert ProductCharacteristic.objects.count() == count_char - 2


@pytest.mark.django_db
def test_update_stock_no_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    data = {"quantity": 0}
    response = client.patch(f"/api/v1/stocks/{tomato.id}/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_stock_wrong_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    data = {"quantity": 0}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{half_base["vegsupplier"]}')
    response = client.patch(f"/api/v1/stocks/{tomato.id}/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_update_stock_admin_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    data = {"quantity": 0}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["admin"]}')
    response = client.patch(f"/api/v1/stocks/{tomato.id}/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_stock_purchaser_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    data = {"quantity": 0}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.patch(f"/api/v1/stocks/{tomato.id}/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_stock_other_supplier_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    data = {"quantity": 0}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["grainsupplier"]}')
    response = client.patch(f"/api/v1/stocks/{tomato.id}/", data=data, format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_update_stock_supplier_token(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    data = {"quantity": 0}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(f"/api/v1/stocks/{tomato.id}/", data=data, format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["quantity"] == data["quantity"]


@pytest.mark.django_db
def test_update_stock_product(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    data = {"quantity": 0, "product": (tomato.product.id + 1)}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(f"/api/v1/stocks/{tomato.id}/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "Stocks product and supplier cannot be amended"}


@pytest.mark.django_db
def test_update_stock_supplier(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    sup = Supplier.objects.filter(name="Аладушкин").first()
    data = {"quantity": 0, "supplier": sup.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(f"/api/v1/stocks/{tomato.id}/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "Stocks product and supplier cannot be amended"}


@pytest.mark.django_db
def test_update_stock_not_unique(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()

    Stock.objects.create(
        product=Product.objects.filter(name="Помидор").first(),
        supplier=Supplier.objects.filter(name="Выборжец").first(),
        quantity=1000,
        price=150,
        price_rrc=200,
        sku="new",
    )
    data = {"sku": "new"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(f"/api/v1/stocks/{tomato.id}/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "Stock with this sku and product already exists"}


@pytest.mark.django_db
def test_update_stock_odd_quantity(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    data = {"quantity": "new"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(f"/api/v1/stocks/{tomato.id}/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"quantity": ["A valid integer is required."]}


@pytest.mark.django_db
def test_update_stock_odd_price(client, half_base):
    tomato = Stock.objects.filter(product__name="Помидор").first()
    data = {"price": "new"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["vegsupplier"]}')
    response = client.patch(f"/api/v1/stocks/{tomato.id}/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"price": ["A valid number is required."]}


@pytest.mark.django_db
def test_update_stock_filter_category(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.get(f"/api/v1/stocks/?product__category__name=Сок", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 5


@pytest.mark.django_db
def test_update_stock_search_address(client, half_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {half_base["minimarket"]}')
    response = client.get(f"/api/v1/stocks/?search=Санкт-Петербург", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 11
