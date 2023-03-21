import pytest

from procurement_supply.models import PasswordResetToken, User


@pytest.mark.django_db
def test_obtain_auth_token(client, user_w_hashed_password):
    data = {
        "username": user_w_hashed_password["username"],
        "password": user_w_hashed_password["password"],
    }
    response = client.post("/api/v1/authorize/", data=data, format="json")
    assert response.status_code == 200
    assert "token" in response.json()


@pytest.mark.django_db
def test_obtain_auth_token_no_username(client, user_w_hashed_password):
    data = {"password": user_w_hashed_password["password"]}
    response = client.post("/api/v1/authorize/", data=data, format="json")
    assert response.status_code == 400
    assert response.json() == {"username": ["This field is required."]}


@pytest.mark.django_db
def test_obtain_auth_token_no_password(client, user_w_hashed_password):
    data = {"username": user_w_hashed_password["username"]}
    response = client.post("/api/v1/authorize/", data=data, format="json")
    assert response.status_code == 400
    assert response.json() == {"password": ["This field is required."]}


@pytest.mark.django_db
def test_obtain_auth_token_wrong_password(client, user_w_hashed_password):
    data = {
        "username": user_w_hashed_password["username"],
        "password": f"wrong{user_w_hashed_password['password']}",
    }
    response = client.post("/api/v1/authorize/", data=data, format="json")
    assert response.status_code == 400
    assert response.json() == {
        "non_field_errors": ["Unable to log in with provided credentials."]
    }


@pytest.mark.django_db
def test_obtain_auth_token_user_not_exists(client):
    data = {"username": "Bob", "password": "Password1!"}
    response = client.post("/api/v1/authorize/", data=data, format="json")
    assert response.status_code == 400
    assert response.json() == {
        "non_field_errors": ["Unable to log in with provided credentials."]
    }


@pytest.mark.django_db
def test_reset_no_username(client):
    response = client.post("/api/v1/password_reset/", data={}, format="json")
    assert response.status_code == 400
    assert response.json() == {
        "error": '"username" field is required for reset token obtain'
    }


@pytest.mark.django_db
def test_reset_user_not_exists(client):
    response = client.post(
        "/api/v1/password_reset/", data={"username": "Bob"}, format="json"
    )
    assert response.status_code == 400
    assert response.json() == {"error": "User with such username does not exist"}


@pytest.mark.django_db
def test_reset_user(client, user_factory):
    user = user_factory(_quantity=1)
    count = PasswordResetToken.objects.all().count()
    response = client.post(
        "/api/v1/password_reset/", data={"username": user[0].username}, format="json"
    )
    assert response.status_code == 200
    assert response.json() == {
        "success": "Reset token is sent to your email."
    }
    assert PasswordResetToken.objects.all().count() == count + 1


@pytest.mark.django_db
def test_reset_user_token_exists(client, user_factory):
    user = user_factory(_quantity=1)
    count = PasswordResetToken.objects.all().count()
    response = client.post(
        "/api/v1/password_reset/", data={"username": user[0].username}, format="json"
    )
    assert response.status_code == 200
    assert response.json() == {
        "success": "Reset token is sent to your email."
    }
    assert PasswordResetToken.objects.all().count() == count + 1
    response = client.post(
        "/api/v1/password_reset/", data={"username": user[0].username}, format="json"
    )
    assert response.status_code == 200
    assert response.json() == {
        "success": "Reset token is sent to your email."
    }
    assert PasswordResetToken.objects.all().count() == count + 1


@pytest.mark.django_db
def test_reset_user_token_no_username(client, user_factory):
    user = user_factory(_quantity=1)
    client.post(
        "/api/v1/password_reset/", data={"username": user[0].username}, format="json"
    )
    token = PasswordResetToken.objects.get(user=user[0].id).token
    response = client.post(
        "/api/v1/password_reset/",
        data={"token": token, "new_password": "StrongPassword1!"},
        format="json",
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": '"username" and "new_password" fields are required for set of new password'
    }


@pytest.mark.django_db
def test_reset_user_token_no_new_password(client, user_factory):
    user = user_factory(_quantity=1)
    client.post(
        "/api/v1/password_reset/", data={"username": user[0].username}, format="json"
    )
    token = PasswordResetToken.objects.get(user=user[0].id).token
    response = client.post(
        "/api/v1/password_reset/",
        data={"token": token, "username": user[0].username},
        format="json",
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": '"username" and "new_password" fields are required for set of new password'
    }


@pytest.mark.django_db
def test_reset_user_token_user_not_exists(client, user_factory):
    user = user_factory(_quantity=1)
    client.post(
        "/api/v1/password_reset/", data={"username": user[0].username}, format="json"
    )
    token = PasswordResetToken.objects.get(user=user[0].id).token
    response = client.post(
        "/api/v1/password_reset/",
        data={
            "token": token,
            "username": "username",
            "new_password": "StrongPassword1!",
        },
        format="json",
    )
    assert response.status_code == 400
    assert response.json() == {"error": "User with such username does not exist"}


@pytest.mark.django_db
def test_reset_user_token_wrong_uuid(client, user_factory):
    user = user_factory(_quantity=1)
    client.post(
        "/api/v1/password_reset/", data={"username": user[0].username}, format="json"
    )
    response = client.post(
        "/api/v1/password_reset/",
        data={
            "token": "wrong",
            "username": user[0].username,
            "new_password": "StrongPassword1!",
        },
        format="json",
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Wrong token"}


@pytest.mark.django_db
def test_reset_user_token_wrong(client, user_factory):
    user = user_factory(_quantity=1)
    client.post(
        "/api/v1/password_reset/", data={"username": user[0].username}, format="json"
    )
    response = client.post(
        "/api/v1/password_reset/",
        data={
            "token": "3065816f-cfdc-47c2-8909-591e013a74a2",
            "username": user[0].username,
            "new_password": "StrongPassword1!",
        },
        format="json",
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Wrong token"}


@pytest.mark.django_db
def test_reset_user_token_user_dont_match(client, user_factory):
    user = user_factory(_quantity=2)
    client.post(
        "/api/v1/password_reset/", data={"username": user[0].username}, format="json"
    )
    token = PasswordResetToken.objects.get(user=user[0].id).token
    response = client.post(
        "/api/v1/password_reset/",
        data={
            "token": token,
            "username": user[1].username,
            "new_password": "StrongPassword1!",
        },
        format="json",
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Wrong token"}


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
def test_reset_user_token_user_password_validation(
    client, user_factory, password, expected_reply
):
    user = user_factory(_quantity=1)
    client.post(
        "/api/v1/password_reset/", data={"username": user[0].username}, format="json"
    )
    token = PasswordResetToken.objects.get(user=user[0].id).token
    response = client.post(
        "/api/v1/password_reset/",
        data={"token": token, "username": user[0].username, "new_password": password},
        format="json",
    )
    assert response.status_code == 400
    assert response.json() == expected_reply


@pytest.mark.django_db
def test_reset_user_token_success(client, user_factory):
    user = user_factory(_quantity=1)
    client.post(
        "/api/v1/password_reset/", data={"username": user[0].username}, format="json"
    )
    old_password = User.objects.get(id=user[0].id).password
    token = PasswordResetToken.objects.get(user=user[0].id).token
    response = client.post(
        "/api/v1/password_reset/",
        data={
            "token": token,
            "username": user[0].username,
            "new_password": "VeryStrongPassword1!",
        },
        format="json",
    )
    assert response.status_code == 200
    assert response.json() == {"success": "Your password has been changed"}
    assert not PasswordResetToken.objects.filter(user=user[0].id).exists()
    assert old_password != User.objects.get(id=user[0].id).password
