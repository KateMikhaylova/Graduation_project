import pytest

from procurement_supply.models import (OrderPosition,  Stock)


@pytest.mark.django_db
def test_list_order_position_no_token(client, full_base):
    response = client.get("/api/v1/order_positions/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_order_position_wrong_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["admin"]}')
    response = client.get("/api/v1/order_positions/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_list_order_position_admin_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.get("/api/v1/order_positions/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 19


@pytest.mark.django_db
def test_list_order_position_purchaser_no_order_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["micromarket"]}')
    response = client.get("/api/v1/order_positions/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 0


@pytest.mark.django_db
def test_list_order_position_supplier_no_order_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["breadsupplier"]}')
    response = client.get("/api/v1/order_positions/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 0


@pytest.mark.django_db
def test_list_order_position_purchaser_with_order_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.get("/api/v1/order_positions/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 10


@pytest.mark.django_db
def test_list_order_position_supplier_with_order_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.get("/api/v1/order_positions/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 6


@pytest.mark.django_db
def test_list_order_position_filter_cancelled(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["grainsupplier"]}')
    response = client.get("/api/v1/order_positions/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 1
    response = client.get("/api/v1/order_positions/?order__status=saved", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 0
    response = client.get(
        "/api/v1/order_positions/?order__status=cancelled", format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 1


@pytest.mark.django_db
def test_retrieve_order_position_no_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    response = client.get(f"/api/v1/order_positions/{position.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_order_position_wrong_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["admin"]}')
    response = client.get(f"/api/v1/order_positions/{position.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_retrieve_order_position_admin_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.get(f"/api/v1/order_positions/{position.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["price"] == "150.00"
    assert reply["quantity"] == 1000
    assert reply["confirmed"]
    assert not reply["delivered"]
    assert (
        Stock.objects.filter(product__name="Помидор").first().id == reply["stock"]["id"]
    )


@pytest.mark.django_db
def test_retrieve_order_position_other_purchaser_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.get(f"/api/v1/order_positions/{position.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_retrieve_order_position_other_supplier_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["grainsupplier"]}')
    response = client.get(f"/api/v1/order_positions/{position.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_retrieve_order_position_owner_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.get(f"/api/v1/order_positions/{position.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["price"] == "150.00"
    assert reply["quantity"] == 1000
    assert reply["confirmed"]
    assert not reply["delivered"]
    assert (
        Stock.objects.filter(product__name="Помидор").first().id == reply["stock"]["id"]
    )


@pytest.mark.django_db
def test_retrieve_order_position_supplier_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.get(f"/api/v1/order_positions/{position.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["price"] == "150.00"
    assert reply["quantity"] == 1000
    assert reply["confirmed"]
    assert not reply["delivered"]
    assert (
        Stock.objects.filter(product__name="Помидор").first().id == reply["stock"]["id"]
    )


@pytest.mark.django_db
def test_update_order_position_no_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    data = {"delivered": True}
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_order_position_wrong_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    data = {"delivered": True}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_update_order_position_admin_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    data = {"delivered": True}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_order_position_purchaser_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    data = {"delivered": True}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_order_position_other_supplier_token(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    data = {"delivered": True}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["grainsupplier"]}')
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_update_order_position_no_data(client, full_base):
    position = OrderPosition.objects.filter(price=150, quantity=1000).first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.patch(f"/api/v1/order_positions/{position.id}/", format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "You can amend confirmed or/and delivered status"}


@pytest.mark.django_db
def test_update_order_position_cancelled(client, full_base):
    position = OrderPosition.objects.filter(price=90, quantity=1000).first()
    data = {"delivered": True}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["grainsupplier"]}')
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "error": "You cannot confirm and deliver cancelled order positions"
    }


@pytest.mark.django_db
def test_update_order_position_odd_confirmed(client, full_base):
    position = OrderPosition.objects.filter(price=100, quantity=100).first()
    data = {"confirmed": "True"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["juice1supplier"]}')
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"confirmed": ["Must be a valid boolean."]}


@pytest.mark.django_db
def test_update_order_position_supplier_token_confirmed(client, full_base):
    position = OrderPosition.objects.filter(
        stock__product__name="Aqua minerale"
    ).first()
    data = {"confirmed": True}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["juice1supplier"]}')
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply == {"success": "Оrder position successfully amended"}
    assert (
        OrderPosition.objects.filter(stock__product__name="Aqua minerale")
        .first()
        .confirmed
    )


@pytest.mark.django_db
def test_update_order_position_unconfirm(client, full_base):
    position = OrderPosition.objects.filter(quantity=200, price=150).first()
    data = {"confirmed": False}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "Your cannot revoke your confirmation"}
    assert OrderPosition.objects.filter(quantity=200, price=150).first().confirmed


@pytest.mark.django_db
def test_update_order_position_odd_delivered(client, full_base):
    position = OrderPosition.objects.filter(price=100, quantity=100).first()
    data = {"delivered": "True"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["juice1supplier"]}')
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"delivered": ["Must be a valid boolean."]}


@pytest.mark.django_db
def test_update_order_position_supplier_token_confirmed(client, full_base):
    position = OrderPosition.objects.filter(
        stock__product__name="Aqua minerale"
    ).first()
    data = {"delivered": True}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["juice1supplier"]}')
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply == {"success": "Оrder position successfully amended"}
    assert (
        OrderPosition.objects.filter(stock__product__name="Aqua minerale")
        .first()
        .delivered
    )


@pytest.mark.django_db
def test_update_order_position_undeliver(client, full_base):
    position = OrderPosition.objects.filter(quantity=500, price=100).first()
    data = {"delivered": False}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["juice1supplier"]}')
    response = client.patch(
        f"/api/v1/order_positions/{position.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"error": "Your cannot revoke your delivery"}
    assert OrderPosition.objects.filter(quantity=500, price=100).first().delivered
