import pytest

from procurement_supply.models import Supplier, User


@pytest.mark.django_db
def test_create_supplier(client, users_base):
    count = Supplier.objects.count()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["breadsupplier"]}')
    data = {"name": "Каравай", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/suppliers/", data=data, format="json")
    assert response.status_code == 201
    assert Supplier.objects.count() == count + 1
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_create_supplier_no_address(client, users_base):
    count = Supplier.objects.count()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["breadsupplier"]}')
    data = {"name": "Каравай"}
    response = client.post("/api/v1/suppliers/", data=data, format="json")
    assert response.status_code == 201
    assert Supplier.objects.count() == count + 1
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_create_supplier_no_name(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["breadsupplier"]}')
    data = {"address": "Санкт-Петербург"}
    response = client.post("/api/v1/suppliers/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"name": ["This field is required."]}


@pytest.mark.django_db
def test_create_supplier_admin_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["admin"]}')
    data = {"name": "Каравай", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/suppliers/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_supplier_purchaser_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["micromarket"]}')
    data = {"name": "Каравай", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/suppliers/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_supplier_no_token(client, users_base):
    data = {"name": "Каравай", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/suppliers/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_create_supplier_wrong_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{users_base["breadsupplier"]}')
    data = {"name": "Каравай", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/suppliers/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_create_supplier_exists(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["grainsupplier"]}')
    data = {"name": "Каравай", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/suppliers/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"user": ["Поставщик with this user already exists."]}


@pytest.mark.django_db
def test_create_supplier_order_true(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["breadsupplier"]}')
    data = {"name": "Каравай", "address": "Санкт-Петербург", "order_status": True}
    response = client.post("/api/v1/suppliers/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["order_status"]


@pytest.mark.django_db
def test_create_supplier_order_false(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["breadsupplier"]}')
    data = {"name": "Каравай", "address": "Санкт-Петербург", "order_status": False}
    response = client.post("/api/v1/suppliers/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert not reply["order_status"]


@pytest.mark.django_db
def test_create_supplier_put_another_user(client, users_base, user_factory):
    user = user_factory(_quantity=1)
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["breadsupplier"]}')
    data = {
        "user": user[0].id,
        "name": "Каравай",
        "address": "Санкт-Петербург",
        "order_status": True,
    }
    response = client.post("/api/v1/suppliers/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["user"] != user[0].id


@pytest.mark.django_db
def test_list_admin_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["admin"]}')
    response = client.get("/api/v1/suppliers/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 4


@pytest.mark.django_db
def test_list_purchaser_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["minimarket"]}')
    response = client.get("/api/v1/suppliers/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 4


@pytest.mark.django_db
def test_list_supplier_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["grainsupplier"]}')
    response = client.get("/api/v1/suppliers/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 1


@pytest.mark.django_db
def test_list_supplier_no_instance_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["breadsupplier"]}')
    response = client.get("/api/v1/suppliers/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 0


@pytest.mark.django_db
def test_list_no_token(client, users_base):
    response = client.get("/api/v1/suppliers/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_supplier_wrong_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{users_base["admin"]}')
    response = client.get("/api/v1/suppliers/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_retrieve_supplier_no_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    response = client.get(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_supplier_wrong_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{users_base["admin"]}')
    response = client.get(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_retrieve_supplier_admin_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["admin"]}')
    response = client.get(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == "Выборжец"


@pytest.mark.django_db
def test_retrieve_supplier_purchaser_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["hypermarket"]}')
    response = client.get(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == "Выборжец"


@pytest.mark.django_db
def test_retrieve_supplier_owner_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["vegsupplier"]}')
    response = client.get(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == "Выборжец"


@pytest.mark.django_db
def test_retrieve_supplier_other_supplier_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["grainsupplier"]}')
    response = client.get(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_destroy_supplier_no_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    response = client.delete(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_destroy_supplier_wrong_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{users_base["admin"]}')
    response = client.delete(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_destroy_supplier_admin_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["admin"]}')
    response = client.delete(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 204
    assert not Supplier.objects.filter(name="Выборжец").first().order_status


@pytest.mark.django_db
def test_destroy_supplier_purchaser_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["hypermarket"]}')
    response = client.delete(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_supplier_owner_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["vegsupplier"]}')
    response = client.delete(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_supplier_other_supplier_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["grainsupplier"]}')
    response = client.delete(f"/api/v1/suppliers/{supplier.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_supplier_no_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    data = {"name": "Овощной", "address": "Санкт-Петербург", "order_status": False}
    response = client.patch(
        f"/api/v1/suppliers/{supplier.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_supplier_wrong_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    data = {"name": "Овощной", "address": "Санкт-Петербург", "order_status": False}
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{users_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/suppliers/{supplier.id}/", data=data, format="json"
    )
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_update_supplier_admin_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    data = {"name": "Овощной", "address": "Санкт-Петербург", "order_status": False}
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["admin"]}')
    response = client.patch(
        f"/api/v1/suppliers/{supplier.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_supplier_purchaser_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    data = {"name": "Овощной", "address": "Санкт-Петербург", "order_status": False}
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["minimarket"]}')
    response = client.patch(
        f"/api/v1/suppliers/{supplier.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_supplier_other_supplier_token(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    data = {"name": "Овощной", "address": "Санкт-Петербург", "order_status": False}
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["grainsupplier"]}')
    response = client.patch(
        f"/api/v1/suppliers/{supplier.id}/", data=data, format="json"
    )
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_update_supplier_success(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    data = {"name": "Овощной", "address": "Санкт-Петербург", "order_status": False}
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/suppliers/{supplier.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == "Овощной"
    assert reply["address"] == "Санкт-Петербург"
    assert not reply["order_status"]


@pytest.mark.django_db
def test_update_supplier_user_patch(client, users_base):
    supplier = Supplier.objects.filter(name="Выборжец").first()
    data = {
        "user": User.objects.get(username="breadsupplier").id,
        "name": "Овощной",
        "address": "Санкт-Петербург",
    }
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["vegsupplier"]}')
    response = client.patch(
        f"/api/v1/suppliers/{supplier.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"error": "user cannot be amended"}


@pytest.mark.django_db
def test_update_supplier_status_wrong_format(client, users_base):
    supplier = Supplier.objects.filter(name="Аладушкин").first()
    data = {"order_status": "да"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["grainsupplier"]}')
    response = client.patch(
        f"/api/v1/suppliers/{supplier.id}/", data=data, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"order_status": ["Must be a valid boolean."]}


@pytest.mark.django_db
def test_update_supplier_status(client, users_base):
    supplier = Supplier.objects.filter(name="Аладушкин").first()
    data = {"order_status": True}
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["grainsupplier"]}')
    response = client.patch(
        f"/api/v1/suppliers/{supplier.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["order_status"]
