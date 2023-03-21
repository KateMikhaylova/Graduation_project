import pytest

from procurement_supply.models import (CartPosition, ShoppingCart, Stock)


@pytest.mark.django_db
def test_list_cart_no_token(client, full_base):
    response = client.get("/api/v1/shopping_carts/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_cart_wrong_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["admin"]}')
    response = client.get("/api/v1/shopping_carts/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_list_cart_admin_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.get("/api/v1/shopping_carts/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 3


@pytest.mark.parametrize(
    ["token", "result"],
    (("hypermarket", 1), ("micromarket", 0), ("supermarket", 1), ("minimarket", 1)),
)
@pytest.mark.django_db
def test_list_cart_purchaser_token(client, full_base, token, result):
    client.credentials(HTTP_AUTHORIZATION=f"Token {full_base[token]}")
    response = client.get("/api/v1/shopping_carts/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == result


@pytest.mark.django_db
def test_list_cart_supplier_no_order_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["breadsupplier"]}')
    response = client.get("/api/v1/shopping_carts/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 0


@pytest.mark.django_db
def test_list_cart_supplier_with_order_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.get("/api/v1/shopping_carts/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 2


@pytest.mark.django_db
def test_retrieve_cart_no_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    response = client.get(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_cart_wrong_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["admin"]}')
    response = client.get(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_retrieve_cart_admin_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.get(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["id"] == cart.id
    assert reply["total_amount"] == 36200
    assert reply["total_quantity"] == 320


@pytest.mark.django_db
def test_retrieve_cart_owner_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.get(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["id"] == cart.id
    assert reply["total_amount"] == 36200
    assert reply["total_quantity"] == 320


@pytest.mark.django_db
def test_retrieve_cart_other_purchaser_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.get(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_retrieve_cart_supplier_no_order_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["breadsupplier"]}')
    response = client.get(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_retrieve_cart_supplier_order_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.get(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["id"] == cart.id
    assert reply["total_amount"] == 36200
    assert reply["total_quantity"] == 320


@pytest.mark.django_db
def test_destroy_cart_no_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    response = client.delete(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_destroy_cart_wrong_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["supermarket"]}')
    response = client.delete(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_destroy_cart_admin_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.delete(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_cart_supplier_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.delete(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_cart_other_purchaser_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="5ка").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.delete(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_destroy_cart_empty_purchaser_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="Фасоль").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.delete(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply == {"success": f"Your shopping cart is empty"}


@pytest.mark.django_db
def test_destroy_cart_full_purchaser_token(client, full_base):
    cart = ShoppingCart.objects.filter(purchaser__name="ОК").first()
    count_tomato = Stock.objects.filter(product__name="Помидор").first().quantity
    count_cucumber = Stock.objects.filter(product__name="Огурец").first().quantity
    count_pepper = Stock.objects.filter(product__name="Перец").first().quantity
    count_positions = CartPosition.objects.count()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.delete(f"/api/v1/shopping_carts/{cart.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply == {"success": f"Your shopping cart is empty"}
    assert CartPosition.objects.filter(shopping_cart=cart.id).count() == 0
    assert CartPosition.objects.count() == count_positions - 3
    assert (
        Stock.objects.filter(product__name="Помидор").first().quantity
        == count_tomato + 100
    )
    assert (
        Stock.objects.filter(product__name="Огурец").first().quantity
        == count_cucumber + 100
    )
    assert (
        Stock.objects.filter(product__name="Перец").first().quantity
        == count_pepper + 100
    )
