# tests/test_users.py
USERS_PREFIX = "/users"
AUTH_PREFIX = "/auth"

def test_invalid_token_authentication(mock_client):
    # attempt to authenticate with invalid token
    invalid_access_token = "invalid_access_token"
    current_user_info_response = mock_client.get(USERS_PREFIX + "/me", headers={"Authorization":f"Bearer {invalid_access_token}"})
    
    current_user_info_status_code = current_user_info_response.status_code
    assert current_user_info_status_code == 401

    current_user_info_json = current_user_info_response.json()
    assert current_user_info_json["detail"] == "Could not validate credentials"

def test_valid_login(mock_client, user_create_payload, user_login_payload):
    # create a user
    user_create_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)
    
    user_create_status_code = user_create_response.status_code
    assert user_create_status_code == 201

    # login for jwt token
    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=user_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 200

    token_type = get_token_response.json()["token_type"]
    assert token_type == "bearer"

    access_token = get_token_response.json()["access_token"]

    # check if token is valid
    current_user_info_response = mock_client.get(USERS_PREFIX + "/me", headers={"Authorization":f"Bearer {access_token}"})
    
    current_user_info_status_code = current_user_info_response.status_code
    assert current_user_info_status_code == 200
    
    current_user_info_response_json = current_user_info_response.json()
    assert current_user_info_response_json["email"] == user_create_payload["email"]

def test_invalid_username_login(mock_client, user_login_payload):
    # login for jwt token with invalid username
    invaid_username_login_payload = user_login_payload.copy()
    invaid_username_login_payload["username"] = "invalid_mock_username"

    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=invaid_username_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 401

    get_token_json = get_token_response.json()
    assert get_token_json["detail"] == "Incorrect email or password"

def test_invalid_password_login(mock_client, user_login_payload):
    # login for jwt token with invalid password
    invaid_password_login_payload = user_login_payload.copy()
    invaid_password_login_payload["password"] = "invalid_mock_password"

    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=invaid_password_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 401

    get_token_json = get_token_response.json()
    assert get_token_json["detail"] == "Incorrect email or password"

