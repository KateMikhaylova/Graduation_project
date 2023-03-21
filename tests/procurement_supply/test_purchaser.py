import pytest

from procurement_supply.models import Purchaser, ShoppingCart, User


@pytest.mark.django_db
def test_create_purchaser(client, users_base):
    count = Purchaser.objects.count()
    count_cart = ShoppingCart.objects.count()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["micromarket"]}')
    data = {"name": "Красное и Белое", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/purchasers/", data=data, format="json")
    assert response.status_code == 201
    assert Purchaser.objects.count() == count + 1
    reply = response.json()
    assert reply["name"] == data["name"]
    assert ShoppingCart.objects.count() == count_cart + 1
    assert (
        ShoppingCart.objects.filter(purchaser=reply["id"]).first().id
        == reply["shopping_cart"]
    )


@pytest.mark.django_db
def test_create_purchaser_no_address(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["micromarket"]}')
    data = {"name": "Красное и Белое"}
    response = client.post("/api/v1/purchasers/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["name"] == data["name"]


@pytest.mark.django_db
def test_create_purchaser_no_name(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["micromarket"]}')
    data = {"address": "Санкт-Петербург"}
    response = client.post("/api/v1/purchasers/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"name": ["This field is required."]}


@pytest.mark.django_db
def test_create_purchaser_admin_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["admin"]}')
    data = {"name": "Красное и Белое", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/purchasers/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_purchaser_supplier_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["vegsupplier"]}')
    data = {"name": "Красное и Белое", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/purchasers/", data=data, format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_create_purchaser_no_token(client, users_base):
    data = {"name": "Красное и Белое", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/purchasers/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_create_purchaser_wrong_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{users_base["micromarket"]}')
    data = {"name": "Красное и Белое", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/purchasers/", data=data, format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_create_purchaser_exists(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["minimarket"]}')
    data = {"name": "Красное и Белое", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/purchasers/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"user": ["Закупщик with this user already exists."]}


@pytest.mark.django_db
def test_create_purchaser_put_another_user(client, users_base, user_factory):
    user = user_factory(_quantity=1)
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["micromarket"]}')
    data = {"user": user[0].id, "name": "Красное и Белое", "address": "Санкт-Петербург"}
    response = client.post("/api/v1/purchasers/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["user"] != user[0].id


@pytest.mark.django_db
def test_list_purchaser_admin_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["admin"]}')
    response = client.get("/api/v1/purchasers/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 3


@pytest.mark.django_db
def test_list_purchaser_purchaser_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["hypermarket"]}')
    response = client.get("/api/v1/purchasers/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 1


@pytest.mark.django_db
def test_list_purchaser_purchaser_no_instance_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["micromarket"]}')
    response = client.get("/api/v1/purchasers/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["count"] == 0


@pytest.mark.django_db
def test_list_purchaser_supplier_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["vegsupplier"]}')
    response = client.get("/api/v1/purchasers/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_list_purchaser_no_token(client, users_base):
    response = client.get("/api/v1/purchasers/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_purchaser_wrong_token(client, users_base):
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{users_base["minimarket"]}')
    response = client.get("/api/v1/purchasers/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_retrieve_purchaser_no_token(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    response = client.get(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_purchaser_wrong_token(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{users_base["minimarket"]}')
    response = client.get(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_retrieve_purchaser_admin_token(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["admin"]}')
    response = client.get(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["id"] == purchaser.id


@pytest.mark.django_db
def test_retrieve_purchaser_supplier_token(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["vegsupplier"]}')
    response = client.get(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_retrieve_purchaser_owner_token(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["minimarket"]}')
    response = client.get(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 200
    reply = response.json()
    assert reply["id"] == purchaser.id


@pytest.mark.django_db
def test_retrieve_purchaser_other_purchaser_token(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["supermarket"]}')
    response = client.get(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_destroy_purchaser(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["admin"]}')
    response = client.delete(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 405
    reply = response.json()
    assert reply == {"detail": 'Method "DELETE" not allowed.'}


@pytest.mark.django_db
def test_update_purchaser_no_token(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    response = client.patch(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_purchaser_wrong_token(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token wrong{users_base["minimarket"]}')
    response = client.patch(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 401
    reply = response.json()
    assert reply == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_update_purchaser_admin_token(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["admin"]}')
    response = client.patch(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_purchaser_supplier_token(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["vegsupplier"]}')
    response = client.patch(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_update_purchaser_other_purchaser_token(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["supermarket"]}')
    response = client.patch(f"/api/v1/purchasers/{purchaser.id}/", format="json")
    assert response.status_code == 404
    reply = response.json()
    assert reply == {"detail": "Not found."}


@pytest.mark.django_db
def test_update_purchaser_success(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    data = {"name": "Фасолька", "address": "Ленинградская область"}
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["minimarket"]}')
    response = client.patch(
        f"/api/v1/purchasers/{purchaser.id}/", data=data, format="json"
    )
    assert response.status_code == 200
    reply = response.json()
    assert reply["name"] == "Фасолька"
    assert reply["address"] == "Ленинградская область"


@pytest.mark.django_db
def test_update_purchaser_user_patch(client, users_base):
    purchaser = Purchaser.objects.filter(name="Фасоль").first()
    data = {
        "user": User.objects.get(username="hypermarket").id,
        "name": "Фасолька",
        "address": "Ленинградская область",
    }
    client.credentials(HTTP_AUTHORIZATION=f'Token {users_base["minimarket"]}')
    response = client.patch(
        f"/api/v1/purchasers/{purchaser.id}/", data=data, format="json"
    )
    assert response.status_code == 403
    reply = response.json()
    assert reply == {"error": "user cannot be amended"}
