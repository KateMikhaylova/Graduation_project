import pytest

from procurement_supply.models import (ChainStore, Order, OrderPosition, Purchaser)


@pytest.mark.django_db
def test_create_chain_store_no_token(client, full_base):
    data = {"name": "name", "address": "address", "phone": "89119111111"}
    response = client.post("/api/v1/chain_stores/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_create_chain_store_wrong_token(client, full_base):
    data = {"name": "name", "address": "address", "phone": "89119111111"}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["minimarket"]}')
    response = client.post("/api/v1/chain_stores/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_create_chain_store_admin_token(client, full_base):
    data = {"name": "name", "address": "address", "phone": "89119111111"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.post("/api/v1/chain_stores/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_chain_store_supplier_token(client, full_base):
    data = {"name": "name", "address": "address", "phone": "89119111111"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.post("/api/v1/chain_stores/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_chain_store_purchaser_no_instance_token(client, full_base):
    data = {"name": "name", "address": "address", "phone": "89119111111"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["micromarket"]}')
    response = client.post("/api/v1/chain_stores/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {
        "error": "you need to create Purchaser before you create or update ChainStore"
    }


@pytest.mark.django_db
def test_create_chain_store_purchaser_token(client, full_base):
    count = ChainStore.objects.count()
    data = {"name": "name", "address": "address", "phone": "89119111111"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.post("/api/v1/chain_stores/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["name"] == data["name"]
    assert ChainStore.objects.count() == count + 1


@pytest.mark.django_db
def test_create_chain_store_put_another_purchaser(client, full_base):
    another = Purchaser.objects.filter(name="Фасоль").first()
    data = {
        "supplier": another.id,
        "name": "name",
        "address": "address",
        "phone": "89119111111",
    }
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.post("/api/v1/chain_stores/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["name"] == data["name"]
    assert reply["purchaser"] != another.id


@pytest.mark.django_db
def test_create_chain_store_no_name(client, full_base):
    data = {"address": "address", "phone": "89119111111"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.post("/api/v1/chain_stores/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"name": ["This field is required."]}


@pytest.mark.django_db
def test_create_chain_store_no_address(client, full_base):
    data = {"name": "name", "phone": "89119111111"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.post("/api/v1/chain_stores/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"address": ["This field is required."]}


@pytest.mark.django_db
def test_create_chain_store_no_phone(client, full_base):
    data = {"name": "name", "address": "address"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.post("/api/v1/chain_stores/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"phone": ["This field is required."]}


@pytest.mark.django_db
def test_list_chain_store_no_token(client, full_base):
    response = client.get("/api/v1/chain_stores/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_chain_store_wrong_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["admin"]}')
    response = client.get("/api/v1/chain_stores/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_list_chain_store_admin_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.get("/api/v1/chain_stores/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 4


@pytest.mark.django_db
def test_list_chain_store_purchaser_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["hypermarket"]}')
    response = client.get("/api/v1/chain_stores/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 3


@pytest.mark.django_db
def test_list_chain_store_purchaser_no_store_token(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.get("/api/v1/chain_stores/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 0


@pytest.mark.django_db
def test_list_chain_store_supplier(client, full_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["juice1supplier"]}')
    response = client.get("/api/v1/chain_stores/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 4


@pytest.mark.django_db
def test_retrieve_chain_store_no_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    response = client.get(f"/api/v1/chain_stores/{lenin.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_chain_store_wrong_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["supermarket"]}')
    response = client.get(f"/api/v1/chain_stores/{lenin.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_retrieve_chain_store_admin_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.get(f"/api/v1/chain_stores/{lenin.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["id"] == lenin.id


@pytest.mark.django_db
def test_retrieve_chain_store_owner_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.get(f"/api/v1/chain_stores/{lenin.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["id"] == lenin.id


@pytest.mark.django_db
def test_retrieve_chain_store_other_purchaser_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.get(f"/api/v1/chain_stores/{lenin.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_retrieve_chain_store_supplier(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["juice1supplier"]}')
    response = client.get(f"/api/v1/chain_stores/{lenin.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["id"] == lenin.id


@pytest.mark.django_db
def test_destroy_chain_store_no_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    response = client.delete(f"/api/v1/chain_stores/{lenin.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_destroy_chain_store_wrong_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["admin"]}')
    response = client.delete(f"/api/v1/chain_stores/{lenin.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_destroy_chain_store_purchaser_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.delete(f"/api/v1/chain_stores/{lenin.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_chain_store_supplier_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.delete(f"/api/v1/chain_stores/{lenin.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_chain_store_admin_token(client, full_base):
    count_store = ChainStore.objects.count()
    count_orders = Order.objects.count()
    count_positions = OrderPosition.objects.count()
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.delete(f"/api/v1/chain_stores/{lenin.id}/", format="json")
    assert response.status_code == 204
    assert ChainStore.objects.count() == count_store - 1
    assert Order.objects.count() == count_orders - 4
    assert OrderPosition.objects.count() == count_positions - 9


@pytest.mark.django_db
def test_update_chain_store_no_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    data = {"name": "patch", "address": "patch", "phone": "patch"}
    response = client.patch(
        f"/api/v1/chain_stores/{lenin.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_chain_store_wrong_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    data = {"name": "patch", "address": "patch", "phone": "patch"}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{full_base["supermarket"]}')
    response = client.patch(
        f"/api/v1/chain_stores/{lenin.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_update_chain_store_admin_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    data = {"name": "patch", "address": "patch", "phone": "patch"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["admin"]}')
    response = client.patch(
        f"/api/v1/chain_stores/{lenin.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_chain_store_supplier_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    data = {"name": "patch", "address": "patch", "phone": "patch"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/chain_stores/{lenin.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_chain_store_other_purchaser_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    data = {"name": "patch", "address": "patch", "phone": "patch"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["minimarket"]}')
    response = client.patch(
        f"/api/v1/chain_stores/{lenin.id}/", data=data, format="json"
    )
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_update_chain_store_purchaser_token(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    data = {"name": "patch", "address": "patch", "phone": "patch"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.patch(
        f"/api/v1/chain_stores/{lenin.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_update_chain_store_put_other_purchaser(client, full_base):
    lenin = ChainStore.objects.filter(name="Ленинский").first()
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    data = {
        "purchaser": purchaser.id,
        "name": "patch",
        "address": "patch",
        "phone": "patch",
    }
    client.credentials(HTTP_AUTHORIZATION=f'Token {full_base["supermarket"]}')
    response = client.patch(
        f"/api/v1/chain_stores/{lenin.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["purchaser"] != purchaser.id
