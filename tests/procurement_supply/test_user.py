import pytest
from django.conf import settings

from procurement_supply.models import User

TEST_EMAIL = settings.EMAIL_HOST_USER


@pytest.mark.django_db
def test_create_user(client):
    count = User.objects.count()
    data = {
        "username": "username1",
        "password": "StrongPassword1!",
        "email": TEST_EMAIL,
        "first_name": "first_name",
        "last_name": "last_name",
        "company": "company",
        "position": "position",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 201
    assert User.objects.count() == count + 1
    reply = response.json()
    assert reply["username"] == data["username"]


@pytest.mark.django_db
def test_create_user_exist(client):
    data = {
        "username": "username1",
        "password": "StrongPassword1!",
        "email": TEST_EMAIL,
        "first_name": "first_name",
        "last_name": "last_name",
        "company": "company",
        "position": "position",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["username"] == data["username"]
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"username": ["A user with that username already exists."]}


@pytest.mark.parametrize(
    ["data", "expected_reply"],
    (
        (
            {
                "password": "StrongPassword1!",
                "email": TEST_EMAIL,
                "first_name": "f",
                "last_name": "l",
                "company": "c",
                "position": "p",
            },
            {"username": ["This field is required."]},
        ),
        (
            {
                "username": "1",
                "email": TEST_EMAIL,
                "first_name": "f",
                "last_name": "l",
                "company": "c",
                "position": "p",
            },
            {"password": ["This field is required."]},
        ),
        (
            {
                "username": "1",
                "password": "StrongPassword1!",
                "first_name": "f",
                "last_name": "l",
                "company": "c",
                "position": "p",
            },
            {"email": ["This field is required."]},
        ),
        (
            {
                "username": "1",
                "password": "StrongPassword1!",
                "email": TEST_EMAIL,
                "last_name": "l",
                "company": "c",
                "position": "p",
            },
            {"first_name": ["This field is required."]},
        ),
        (
            {
                "username": "1",
                "password": "StrongPassword1!",
                "email": TEST_EMAIL,
                "first_name": "f",
                "company": "c",
                "position": "p",
            },
            {"last_name": ["This field is required."]},
        ),
        (
            {
                "username": "1",
                "password": "StrongPassword1!",
                "email": TEST_EMAIL,
                "first_name": "f",
                "last_name": "l",
                "position": "p",
            },
            {"company": ["This field is required."]},
        ),
        (
            {
                "username": "1",
                "password": "StrongPassword1!",
                "email": TEST_EMAIL,
                "first_name": "f",
                "last_name": "l",
                "company": "c",
            },
            {"position": ["This field is required."]},
        ),
    ),
)
@pytest.mark.django_db
def test_create_user_less_info(client, data, expected_reply):
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 400
    assert response.json() == expected_reply


@pytest.mark.django_db
def test_create_user_null_username(client):
    data = {
        "username": None,
        "password": "StrongPassword1!",
        "email": TEST_EMAIL,
        "first_name": "first_name",
        "last_name": "last_name",
        "company": "company",
        "position": "position",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"username": ["This field may not be null."]}


@pytest.mark.django_db
def test_create_user_blank_username(client):
    data = {
        "username": "",
        "password": "StrongPassword1!",
        "email": TEST_EMAIL,
        "first_name": "first_name",
        "last_name": "last_name",
        "company": "company",
        "position": "position",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"username": ["This field may not be blank."]}


@pytest.mark.parametrize(
    ["post_type", "result_type"],
    (("purchaser", "purchaser"), ("supplier", "supplier"), ("admin", "admin")),
)
@pytest.mark.django_db
def test_create_user_type(client, post_type, result_type):
    data = {
        "username": "username1",
        "password": "StrongPassword1!",
        "email": TEST_EMAIL,
        "first_name": "first_name",
        "last_name": "last_name",
        "company": "company",
        "position": "position",
        "type": post_type,
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["type"] == result_type


@pytest.mark.django_db
def test_create_user_bad_type(client):
    data = {
        "username": "username1",
        "password": "StrongPassword1!",
        "email": TEST_EMAIL,
        "first_name": "first_name",
        "last_name": "last_name",
        "company": "company",
        "position": "position",
        "type": "other",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"type": ['"other" is not a valid choice.']}


@pytest.mark.django_db
def test_create_user_no_type(client):
    data = {
        "username": "username1",
        "password": "StrongPassword1!",
        "email": TEST_EMAIL,
        "first_name": "first_name",
        "last_name": "last_name",
        "company": "company",
        "position": "position",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 201
    reply = response.json()
    assert reply["type"] == "purchaser"


@pytest.mark.django_db
def test_create_user_bad_email(client):
    data = {
        "username": "username1",
        "password": "StrongPassword1!",
        "email": "123",
        "first_name": "first_name",
        "last_name": "last_name",
        "company": "company",
        "position": "position",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"email": ["Enter a valid email address."]}


@pytest.mark.parametrize(
    ["password", "expected_reply"],
    (
        (
            "93825647895217321596227862362245821005",
            {"error": ["This password is entirely numeric."]},
        ),
        (
            "strpas1",
            {
                "error": [
                    "This password is too short. It must contain at least 8 characters."
                ]
            },
        ),
        ("password", {"error": ["This password is too common."]}),
    ),
)
@pytest.mark.django_db
def test_create_user_bad_password(client, password, expected_reply):
    data = {
        "username": "username1",
        "password": password,
        "email": TEST_EMAIL,
        "first_name": "first_name",
        "last_name": "last_name",
        "company": "company",
        "position": "position",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == expected_reply


@pytest.mark.django_db
def test_list_users_no_token(client):
    response = client.get("/api/v1/users/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_users_wrong_token(client, admin_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token wrong{admin_auth.key}")
    response = client.get("/api/v1/users/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_list_users_admin(client, admin_auth, user_factory):
    users = user_factory(_quantity=5)
    client.credentials(HTTP_AUTHORIZATION=f"Token {admin_auth.key}")
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(users) + 1 == data["count"]
    for i, user in enumerate(data["results"]):
        if i == 0:
            assert user["id"] == admin_auth.user_id
        else:
            assert user["username"] == users[i - 1].username


@pytest.mark.django_db
def test_list_users_user_token(client, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {purchaser_auth.key}")
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["results"][0]["id"] == purchaser_auth.user_id


@pytest.mark.django_db
def test_retrieve_user_no_token(client, purchaser_auth):
    response = client.get(f"/api/v1/users/{purchaser_auth.user_id}/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_user_wrong_token(client, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token wrong{purchaser_auth.key}")
    response = client.get(f"/api/v1/users/{purchaser_auth.user_id}/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_retrieve_user_admin(client, purchaser_auth, admin_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {admin_auth.key}")
    response = client.get(f"/api/v1/users/{purchaser_auth.user_id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == purchaser_auth.user_id
    assert "username" in data


@pytest.mark.django_db
def test_retrieve_user_token(client, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {purchaser_auth.key}")
    response = client.get(f"/api/v1/users/{purchaser_auth.user_id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == purchaser_auth.user_id
    assert "username" in data


@pytest.mark.django_db
def test_retrieve_user_anothers_token(client, purchaser_auth, supplier_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {supplier_auth.key}")
    response = client.get(f"/api/v1/users/{purchaser_auth.user_id}/")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Not found."}


@pytest.mark.django_db
def test_delete_user_no_token(client, user_factory):
    user = user_factory(_quantity=1)
    response = client.delete(f"/api/v1/users/{user[0].id}/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_delete_user_wrong_token(client, user_factory, admin_auth):
    user = user_factory(_quantity=1)
    client.credentials(HTTP_AUTHORIZATION=f"Token wrong{admin_auth.key}")
    response = client.delete(f"/api/v1/users/{user[0].id}/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_delete_user_others_token(client, user_factory, purchaser_auth):
    user = user_factory(_quantity=1)
    client.credentials(HTTP_AUTHORIZATION=f"Token {purchaser_auth.key}")
    response = client.delete(f"/api/v1/users/{user[0].id}/")
    assert response.status_code == 403
    data = response.json()
    assert data == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_delete_user_admin(client, user_factory, admin_auth):
    user = user_factory(_quantity=1)
    client.credentials(HTTP_AUTHORIZATION=f"Token {admin_auth.key}")
    response = client.delete(f"/api/v1/users/{user[0].id}/")
    assert response.status_code == 204
    assert not User.objects.get(id=user[0].id).is_active


@pytest.mark.django_db
def test_patch_user_no_token(client, user_factory):
    user = user_factory(_quantity=1)
    response = client.patch(
        f"/api/v1/users/{user[0].id}/", data={"username": "patch"}, format="json"
    )
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_patch_user_wrong_token(client, user_factory, admin_auth):
    user = user_factory(_quantity=1)
    client.credentials(HTTP_AUTHORIZATION=f"Token wrong{admin_auth.key}")
    response = client.patch(
        f"/api/v1/users/{user[0].id}/", data={"username": "patch"}, format="json"
    )
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Invalid token."}


@pytest.mark.django_db
def test_patch_user_admin_token(client, user_factory, admin_auth):
    user = user_factory(_quantity=1)
    client.credentials(HTTP_AUTHORIZATION=f"Token {admin_auth.key}")
    response = client.patch(
        f"/api/v1/users/{user[0].id}/", data={"username": "patch"}, format="json"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "patch"


@pytest.mark.django_db
def test_patch_user_users_token(client, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {purchaser_auth.key}")
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/",
        data={"username": "patch"},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "patch"


@pytest.mark.django_db
def test_patch_user_others_token(client, purchaser_auth, supplier_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {purchaser_auth.key}")
    response = client.patch(
        f"/api/v1/users/{supplier_auth.user_id}/",
        data={"username": "patch"},
        format="json",
    )
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Not found."}


@pytest.mark.django_db
def test_patch_user_type(client, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {purchaser_auth.key}")
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/",
        data={"type": "admin"},
        format="json",
    )
    assert response.status_code == 403
    data = response.json()
    assert data == {"error": "type cannot be amended"}


@pytest.mark.django_db
def test_patch_user_existing_username(client, purchaser_auth, user_factory):
    user = user_factory(_quantity=1)
    client.credentials(HTTP_AUTHORIZATION=f"Token {purchaser_auth.key}")
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/",
        data={"username": user[0].username},
        format="json",
    )
    assert response.status_code == 400
    data = response.json()
    assert data == {"username": ["A user with that username already exists."]}


@pytest.mark.django_db
def test_patch_user_bad_email(client, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {purchaser_auth.key}")
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/", data={"email": 123}, format="json"
    )
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"email": ["Enter a valid email address."]}


@pytest.mark.django_db
def test_patch_user_password(client, user_w_hashed_password):
    client.credentials(HTTP_AUTHORIZATION=f'Token {user_w_hashed_password["token"]}')
    old_password = User.objects.get(id=user_w_hashed_password["user"]).password
    response = client.patch(
        f'/api/v1/users/{user_w_hashed_password["user"]}/',
        data={"password": "StrongPassword1!", "new_password": "NewStrongPassword1!"},
        format="json",
    )
    assert response.status_code == 200
    assert old_password != User.objects.get(id=user_w_hashed_password["user"]).password


@pytest.mark.django_db
def test_patch_user_password_wrong(client, user_w_hashed_password):
    client.credentials(HTTP_AUTHORIZATION=f'Token {user_w_hashed_password["token"]}')
    response = client.patch(
        f'/api/v1/users/{user_w_hashed_password["user"]}/',
        data={"password": "wrongpassword", "new_password": "NewStrongPassword1!"},
        format="json",
    )
    assert response.status_code == 403
    response = response.json()
    assert response == {"error": "wrong password"}


@pytest.mark.parametrize(
    ["password", "expected_reply"],
    (
        (
            "938256478952173215962278623622458210055",
            {"error": ["This password is entirely numeric."]},
        ),
        (
            "strpas1",
            {
                "error": [
                    "This password is too short. It must contain at least 8 characters."
                ]
            },
        ),
        ("password", {"error": ["This password is too common."]}),
    ),
)
@pytest.mark.django_db
def test_patch_user_password_validation(
    client, user_w_hashed_password, password, expected_reply
):
    client.credentials(HTTP_AUTHORIZATION=f'Token {user_w_hashed_password["token"]}')
    response = client.patch(
        f'/api/v1/users/{user_w_hashed_password["user"]}/',
        data={"password": "StrongPassword1!", "new_password": password},
        format="json",
    )
    assert response.status_code == 400
    assert response.json() == expected_reply


@pytest.mark.django_db
def test_patch_user_is_staff_admin(client, admin_auth, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {admin_auth.key}")
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/",
        data={"is_staff": True},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_staff"]
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/",
        data={"is_staff": False},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["is_staff"]


@pytest.mark.django_db
def test_patch_user_is_staff_not_admin(client, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {purchaser_auth.key}")
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/",
        data={"is_staff": True},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["is_staff"]


@pytest.mark.django_db
def test_patch_user_is_staff_wrong_format(client, admin_auth, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {admin_auth.key}")
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/",
        data={"is_staff": "да"},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["is_staff"]


@pytest.mark.django_db
def test_patch_user_is_superuser_admin(client, admin_auth, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {admin_auth.key}")
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/",
        data={"is_superuser": True},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_superuser"]
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/",
        data={"is_superuser": False},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["is_superuser"]


@pytest.mark.django_db
def test_patch_user_is_superuser_not_admin(client, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {purchaser_auth.key}")
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/",
        data={"is_superuser": True},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["is_superuser"]


@pytest.mark.django_db
def test_patch_user_is_superuser_wrong_format(client, admin_auth, purchaser_auth):
    client.credentials(HTTP_AUTHORIZATION=f"Token {admin_auth.key}")
    response = client.patch(
        f"/api/v1/users/{purchaser_auth.user_id}/",
        data={"is_superuser": "да"},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert not data["is_superuser"]
