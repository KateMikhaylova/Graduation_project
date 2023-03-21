import pytest

from procurement_supply.models import (CartPosition, ShoppingCart, Stock)


@pytest.mark.django_db
def test_create_cart_position_no_token(client, full_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id, "quantity": 100}
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_create_cart_position_wrong_token(client, full_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id, "quantity": 100}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["minimarket"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_create_cart_position_admin_token(client, full_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id, "quantity": 100}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_cart_position_supplier_token(client, full_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id, "quantity": 100}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_cart_position_purchaser_no_instance_token(client, full_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id, "quantity": 100}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["micromarket"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "error": f"You need to create Purchaser and ShoppingCart will be created as well"
    }


@pytest.mark.django_db
def test_create_cart_position_purchaser_has_position_token(client, full_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id, "quantity": 100}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": f"You already have this product in your cart"}


@pytest.mark.django_db
def test_create_cart_position_no_stock(client, full_base):
    data = {"quantity": 100}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": f'Fields "stock" and "quantity" are required'}


@pytest.mark.django_db
def test_create_cart_position_no_quantity(client, full_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": f'Fields "stock" and "quantity" are required'}


@pytest.mark.django_db
def test_create_cart_position_supplier_does_not_receive_orders(client, full_base):
    stock = Stock.objects.filter(product__name="Рис").first()
    data = {"stock": stock.id, "quantity": 100}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": f"This supplier does not take new orders at the moment"}


@pytest.mark.django_db
def test_create_cart_position_not_enough_stock(client, full_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id, "quantity": 10000}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": f"Not enough stock. Only 1000 is available"}


@pytest.mark.django_db
def test_create_cart_position_odd_quantity(client, full_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id, "quantity": -10000}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"quantity": ["Ensure this value is integer and greater than 0."]}


@pytest.mark.django_db
def test_create_cart_position_float_quantity(client, full_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id, "quantity": 1.33}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"quantity": ["Ensure this value is integer and greater than 0."]}


@pytest.mark.django_db
def test_create_cart_position_success(client, full_base):
    stock = Stock.objects.filter(product__name="Помидор").first()
    count_positions = CartPosition.objects.count()
    stock_quantity = stock.quantity
    data = {"stock": stock.id, "quantity": 200}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.post("/api/v1/cart_positions/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert CartPosition.objects.count() == count_positions + 1
    assert reply["stock"] == stock.id
    assert reply["quantity"] == data["quantity"]
    assert reply["amount"] == data["quantity"] * stock.price
    assert (
        Stock.objects.filter(product__name="Помидор").first().quantity
        == stock_quantity - data["quantity"]
    )
    assert (
        ShoppingCart.objects.filter(purchaser__name="Фасоль").first().total_amount
        == reply["amount"]
    )


@pytest.mark.django_db
def test_list_cart_position_no_token(client, full_base):
    response = client.get("/api/v1/cart_positions/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_cart_position_wrong_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["admin"]}')
    response = client.get("/api/v1/cart_positions/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_list_cart_position_admin_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.get("/api/v1/cart_positions/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 7


@pytest.mark.django_db
def test_list_cart_position_purchaser_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.get("/api/v1/cart_positions/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 3


@pytest.mark.django_db
def test_list_cart_position_purchaser_no_instance_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["micromarket"]}')
    response = client.get("/api/v1/cart_positions/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 0


@pytest.mark.django_db
def test_list_cart_position_supplier_wo_orders_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["breadsupplier"]}')
    response = client.get("/api/v1/cart_positions/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 0


@pytest.mark.django_db
def test_list_cart_position_supplier_with_orders_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.get("/api/v1/cart_positions/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 4


@pytest.mark.django_db
def test_retrieve_cart_position_no_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    response = client.get(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_cart_position_wrong_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["admin"]}')
    response = client.get(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_retrieve_cart_position_admin_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.get(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["quantity"] == 50


@pytest.mark.django_db
def test_retrieve_cart_position_other_purchaser_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.get(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_retrieve_cart_position_other_supplier_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.get(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_retrieve_cart_position_owner_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.get(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["quantity"] == 50


@pytest.mark.django_db
def test_retrieve_cart_position_supplier_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["juice1supplier"]}')
    response = client.get(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["quantity"] == 50


@pytest.mark.django_db
def test_destroy_cart_position_no_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    response = client.delete(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_destroy_cart_position_wrong_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["supermarket"]}')
    response = client.delete(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_destroy_cart_position_admin_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.delete(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_cart_position_supplier_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["juice1supplier"]}')
    response = client.delete(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_cart_position_other_purchaser_token(client, full_base):
    position = CartPosition.objects.filter(quantity=50).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.delete(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_destroy_cart_position_purchaser_token(client, full_base):
    position_count = CartPosition.objects.count()
    stock = Stock.objects.filter(
        product__name="Сок апельсиновый", supplier__name="Pepsico"
    ).first()
    stock_quantity = stock.quantity
    cart_amount = (
        ShoppingCart.objects.filter(purchaser__name="5ка").first().total_amount
    )
    position = CartPosition.objects.filter(quantity=50).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.delete(f"/api/v1/cart_positions/{position.id}/", format="json")
    assert response.status_code == 204
    assert CartPosition.objects.count() == position_count - 1
    assert (
        Stock.objects.filter(product__name="Сок апельсиновый", supplier__name="Pepsico")
        .first()
        .quantity
        == stock_quantity + position.quantity
    )
    assert (
        ShoppingCart.objects.filter(purchaser__name="5ка").first().total_amount
        == cart_amount - position.amount
    )


@pytest.mark.django_db
def test_update_cart_position_no_token(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    data = {"quantity": 500}
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_cart_position_wrong_token(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    data = {"quantity": 500}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["hypermarket"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_update_cart_position_admin_token(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    data = {"quantity": 500}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_cart_position_supplier_token(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    data = {"quantity": 500}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_cart_position_other_purchaser_token(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    data = {"quantity": 500}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_update_cart_position_patch_cart(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    data = {"shopping_cart": cart.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": f'Only "quantity" field may be amended'}


@pytest.mark.django_db
def test_update_cart_position_patch_price(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    data = {"price": 1}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": f'Only "quantity" field may be amended'}


@pytest.mark.django_db
def test_update_cart_position_patch_stock(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    stock = Stock.objects.filter(product__name="Помидор").first()
    data = {"stock": stock.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": f'Only "quantity" field may be amended'}


@pytest.mark.django_db
def test_update_cart_position_odd_quantity(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    data = {"quantity": -100}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"quantity": ["Ensure this value is integer and greater than 0."]}


@pytest.mark.django_db
def test_update_cart_position_float_quantity(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    data = {"quantity": 1.33}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"quantity": ["Ensure this value is integer and greater than 0."]}


@pytest.mark.django_db
def test_update_cart_position_less_quantity(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    stock = Stock.objects.filter(product__name="Огурец").first()
    stock_quantity = stock.quantity
    cart_amount = ShoppingCart.objects.filter(purchaser__name="ОК").first().total_amount
    data = {"quantity": 50}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["quantity"] == 50
    assert reply["amount"] == 5000
    assert (
        Stock.objects.filter(product__name="Огурец").first().quantity
        == stock_quantity + data["quantity"]
    )
    assert (
        ShoppingCart.objects.filter(purchaser__name="ОК").first().total_amount
        == cart_amount - 5000
    )


@pytest.mark.django_db
def test_update_cart_position_more_quantity_no_orders(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=120).first()
    data = {"quantity": 150}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": f"This supplier does not take new orders at the moment"}


@pytest.mark.django_db
def test_update_cart_position_more_quantity_no_stock(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    stock = Stock.objects.filter(product__name="Огурец").first()
    data = {"quantity": 10000}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "error": f"Not enough stock. You can add only {stock.quantity} to your initial quantity"
    }


@pytest.mark.django_db
def test_update_cart_position_more_quantity_success(client, full_base):
    position = CartPosition.objects.filter(quantity=100, price=100).first()
    stock = Stock.objects.filter(product__name="Огурец").first()
    stock_quantity = stock.quantity
    cart_amount = ShoppingCart.objects.filter(purchaser__name="ОК").first().total_amount
    data = {"quantity": 1100}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(
        f"/api/v1/cart_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["quantity"] == data["quantity"]
    assert reply["price"] == "130.00"
    assert reply["amount"] == 143000
    updated_stock = Stock.objects.filter(product__name="Огурец").first()
    assert (
        updated_stock.quantity == stock_quantity - data["quantity"] + position.quantity
    )
    assert (
        ShoppingCart.objects.filter(purchaser__name="ОК").first().total_amount
        == cart_amount
        - position.quantity * position.price
        + data["quantity"] * updated_stock.price
    )
