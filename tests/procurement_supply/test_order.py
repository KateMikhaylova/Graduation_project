import pytest

from procurement_supply.models import (CartPosition, ChainStore, Order,
                                       OrderPosition, Purchaser, Stock)


@pytest.mark.django_db
def test_create_order_no_token(client, full_base):
    store = ChainStore.objects.filter(name="Германа").first()
    data = {"chain_store": store.id}
    response = client.post("/api/v1/orders/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_create_order_wrong_token(client, full_base):
    store = ChainStore.objects.filter(name="Германа").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["hypermarket"]}')
    response = client.post("/api/v1/orders/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_create_order_admin_token(client, full_base):
    store = ChainStore.objects.filter(name="Германа").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.post("/api/v1/orders/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_order_supplier_token(client, full_base):
    store = ChainStore.objects.filter(name="Германа").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.post("/api/v1/orders/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_order_purchaser_no_instance_token(client, full_base):
    store = ChainStore.objects.filter(name="Германа").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["micromarket"]}')
    response = client.post("/api/v1/orders/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "error": "you need to create Purchaser before you create or update Orders"
    }


@pytest.mark.django_db
def test_create_order_purchaser_empty_cart_token(client, full_base):
    store = ChainStore.objects.filter(name="Германа").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.post("/api/v1/orders/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "Your shopping cart is empty"}


@pytest.mark.django_db
def test_create_order_purchaser_no_store(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.post("/api/v1/orders/", format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"chain_store": ["This field is required."]}


@pytest.mark.django_db
def test_create_order_purchaser_str_store(client, full_base):
    data = {"chain_store": "store.id"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.post("/api/v1/orders/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "chain_store": ["Incorrect type. Expected pk value, received str."]
    }


@pytest.mark.django_db
def test_create_order_purchaser_odd_store(client, full_base):
    data = {"chain_store": 9999999}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.post("/api/v1/orders/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"chain_store": ['Invalid pk "9999999" - object does not exist.']}


@pytest.mark.django_db
def test_create_order_purchaser_others_store(client, full_base):
    store = ChainStore.objects.filter(name="Германа").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.post("/api/v1/orders/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "Your can order delivery only to your chain stores"}


@pytest.mark.django_db
def test_create_order_purchaser_success(client, full_base):
    count_orders = Order.objects.count()
    count_order_positions = OrderPosition.objects.count()
    count_cart_positions = CartPosition.objects.count()
    store = ChainStore.objects.filter(name="Германа").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.post("/api/v1/orders/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply.get("id")
    assert reply["purchaser"] == Purchaser.objects.filter(name="ОК").first().id
    assert reply["chain_store"] == store.id
    assert reply["status"] == "saved"
    assert reply["total_quantity"] == 300
    assert reply["total_amount"] == 50000
    assert Order.objects.count() == count_orders + 1
    assert OrderPosition.objects.count() == count_order_positions + 3
    assert CartPosition.objects.count() == count_cart_positions - 3
    positions = Order.objects.get(id=reply["id"]).order_positions.all()
    assert positions[0].quantity == 100
    assert positions[0].price == 100
    assert positions[1].quantity == 100
    assert positions[1].price == 150
    assert positions[2].quantity == 100
    assert positions[2].price == 250


@pytest.mark.django_db
def test_create_order_purchaser_success_combined_order_multiplier(client, full_base):
    count_orders = Order.objects.count()
    count_order_positions = OrderPosition.objects.count()
    count_cart_positions = CartPosition.objects.count()
    store = ChainStore.objects.filter(name="Ленинский").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.post("/api/v1/orders/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply.get("id")
    assert reply["purchaser"] == Purchaser.objects.filter(name="5ка").first().id
    assert reply["chain_store"] == store.id
    assert reply["status"] == "saved"
    assert reply["total_quantity"] == 320
    assert reply["total_amount"] == 39820
    assert Order.objects.count() == count_orders + 1
    assert OrderPosition.objects.count() == count_order_positions + 4
    assert CartPosition.objects.count() == count_cart_positions - 4
    positions = Order.objects.get(id=reply["id"]).order_positions.all()
    assert positions[0].quantity == 70
    assert positions[0].price == 60
    assert positions[1].quantity == 50
    assert positions[1].price == 100
    assert positions[2].quantity == 100
    assert positions[2].price == 120
    assert positions[3].quantity == 100
    assert positions[3].price == 150


@pytest.mark.django_db
def test_list_order_no_token(client, full_base):
    response = client.get("/api/v1/orders/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_order_wrong_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["admin"]}')
    response = client.get("/api/v1/orders/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_list_order_admin_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.get("/api/v1/orders/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 7


@pytest.mark.django_db
def test_list_order_purchaser_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.get("/api/v1/orders/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 3


@pytest.mark.django_db
def test_list_order_purchaser_no_instance_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["micromarket"]}')
    response = client.get("/api/v1/orders/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 0


@pytest.mark.django_db
def test_list_order_supplier_wo_orders_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["breadsupplier"]}')
    response = client.get("/api/v1/orders/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 0


@pytest.mark.django_db
def test_list_order_supplier_with_orders_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.get("/api/v1/orders/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 2


@pytest.mark.django_db
def test_retrieve_order_no_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    response = client.get(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_order_wrong_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["admin"]}')
    response = client.get(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_retrieve_order_admin_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.get(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["chain_store"]["name"] == "Жукова"
    assert reply["confirmed"]
    assert not reply["delivered"]
    assert len(reply["order_positions"]) == 3
    assert reply["total_amount"] == 530000
    assert reply["total_quantity"] == 3000


@pytest.mark.django_db
def test_retrieve_order_owner_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.get(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["chain_store"]["name"] == "Жукова"
    assert reply["confirmed"]
    assert not reply["delivered"]
    assert len(reply["order_positions"]) == 3
    assert reply["total_amount"] == 530000
    assert reply["total_quantity"] == 3000


@pytest.mark.django_db
def test_retrieve_order_other_purchaser_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.get(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_retrieve_order_supplier_no_order_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["grainsupplier"]}')
    response = client.get(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_retrieve_order_supplier_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.get(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["chain_store"]["name"] == "Жукова"
    assert reply["confirmed"]
    assert not reply["delivered"]
    assert len(reply["order_positions"]) == 3
    assert reply["total_amount"] == 530000
    assert reply["total_quantity"] == 3000


@pytest.mark.django_db
def test_destroy_order_no_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    response = client.delete(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_destroy_order_wrong_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["hypermarket"]}')
    response = client.delete(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_destroy_order_admin_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.delete(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_order_supplier_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.delete(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_order_other_purchaser_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.delete(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_destroy_order_confirmed_positions(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.delete(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "error": "Your can cancel only fully unconfirmed and undelivered orders"
    }


@pytest.mark.django_db
def test_destroy_order_already_cancelled(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Заневский"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.delete(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "Order is already cancelled"}


@pytest.mark.django_db
def test_destroy_order_success(client, full_base):
    stock1 = (
        Stock.objects.filter(product__name="Сок апельсиновый", supplier__name="Pepsico")
        .first()
        .quantity
    )
    stock2 = (
        Stock.objects.filter(product__name="Сок апельсиновый", supplier__name="Мултон")
        .first()
        .quantity
    )
    stock3 = (
        Stock.objects.filter(product__name="Сок яблочный", supplier__name="Pepsico")
        .first()
        .quantity
    )
    stock4 = (
        Stock.objects.filter(product__name="Сок яблочный", supplier__name="Мултон")
        .first()
        .quantity
    )
    stock5 = (
        Stock.objects.filter(product__name="Сок томатный", supplier__name="Pepsico")
        .first()
        .quantity
    )
    stock6 = (
        Stock.objects.filter(product__name="Сок томатный", supplier__name="Мултон")
        .first()
        .quantity
    )
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Германа"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.delete(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply == {"success": "Order cancelled"}
    assert (
        Order.objects.filter(purchaser__name="ОК", chain_store__name="Германа")
        .first()
        .status
        == "cancelled"
    )
    assert (
        Stock.objects.filter(product__name="Сок апельсиновый", supplier__name="Pepsico")
        .first()
        .quantity
        == stock1 + 100
    )
    assert (
        Stock.objects.filter(product__name="Сок апельсиновый", supplier__name="Мултон")
        .first()
        .quantity
        == stock2 + 100
    )
    assert (
        Stock.objects.filter(product__name="Сок яблочный", supplier__name="Pepsico")
        .first()
        .quantity
        == stock3 + 100
    )
    assert (
        Stock.objects.filter(product__name="Сок яблочный", supplier__name="Мултон")
        .first()
        .quantity
        == stock4 + 100
    )
    assert (
        Stock.objects.filter(product__name="Сок томатный", supplier__name="Pepsico")
        .first()
        .quantity
        == stock5 + 100
    )
    assert (
        Stock.objects.filter(product__name="Сок томатный", supplier__name="Мултон")
        .first()
        .quantity
        == stock6 + 100
    )


@pytest.mark.django_db
def test_update_order_no_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Германа"
    ).first()
    response = client.patch(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_order_wrong_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Германа"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["hypermarket"]}')
    response = client.patch(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_update_order_admin_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Германа"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.patch(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_order_supplier_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Германа"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["juice1supplier"]}')
    response = client.patch(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_order_other_purchaser_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Германа"
    ).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.patch(f"/api/v1/orders/{order.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_update_order_purchaser_token(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Германа"
    ).first()
    store = ChainStore.objects.filter(name="Жукова").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(f"/api/v1/orders/{order.id}/", data=data, format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["chain_store"] == store.id


@pytest.mark.django_db
def test_update_order_odd_store(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Германа"
    ).first()
    data = {"chain_store": "store.id"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(f"/api/v1/orders/{order.id}/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "chain_store": ["Incorrect type. Expected pk value, received str."]
    }


@pytest.mark.django_db
def test_update_order_store_not_exists(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Германа"
    ).first()
    data = {"chain_store": 9999}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(f"/api/v1/orders/{order.id}/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"chain_store": ['Invalid pk "9999" - object does not exist.']}


@pytest.mark.django_db
def test_update_order_cancelled(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Заневский"
    ).first()
    store = ChainStore.objects.filter(name="Жукова").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(f"/api/v1/orders/{order.id}/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "Your cannot amend cancelled order"}


@pytest.mark.django_db
def test_update_order_confirmed(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Жукова"
    ).first()
    store = ChainStore.objects.filter(name="Заневский").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(f"/api/v1/orders/{order.id}/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "error": "Your can amend only fully unconfirmed and undelivered orders"
    }


@pytest.mark.django_db
def test_update_order_purchaser(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Германа"
    ).first()
    data = {"purchaser": Purchaser.objects.filter(name="5ка").first().id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(f"/api/v1/orders/{order.id}/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"error": "Purchaser cannot be amended"}


@pytest.mark.django_db
def test_update_order_others_store(client, full_base):
    order = Order.objects.filter(
        purchaser__name="ОК", chain_store__name="Германа"
    ).first()
    store = ChainStore.objects.filter(name="Ленинский").first()
    data = {"chain_store": store.id}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(f"/api/v1/orders/{order.id}/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "Your can order delivery only to your chain stores"}
