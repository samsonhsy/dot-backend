# tests/test_users.py
USERS_PREFIX = "/users"
AUTH_PREFIX = "/auth"
ADMIN_PREFIX = "/admin"

def test_valid_register(mock_client, user_create_payload):
    # register the user
    user_register_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)
    
    user_register_status_code = user_register_response.status_code    
    assert user_register_status_code == 201

    user_register_json = user_register_response.json()

    assert user_register_json["username"] == user_create_payload["username"]
    assert user_register_json["email"] == user_create_payload["email"]
    assert user_register_json["id"] == 1

    # check if user exists in database after registration
    get_user_list_response = mock_client.get(USERS_PREFIX + "/")
    
    get_user_list_status_code = get_user_list_response.status_code
    assert get_user_list_status_code == 200

    get_user_list_response_json = get_user_list_response.json()
    assert get_user_list_response_json[0]["username"] == user_create_payload["username"]
    assert get_user_list_response_json[0]["email"] == user_create_payload["email"]
    assert get_user_list_response_json[0]["id"] == 1

def test_duplicate_username_register(mock_client, user_create_payload):
    # register a user
    original_register_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)

    original_register_status_code = original_register_response.status_code
    assert original_register_status_code == 201

    # attempt to register a user with the same username but different email
    duplicate_username_create_payload = user_create_payload.copy()
    duplicate_username_create_payload["email"] = "new_mock_email@email.com"

    duplicate_username_register_response = mock_client.post(USERS_PREFIX + "/register", json=duplicate_username_create_payload)
    duplicate_username_register_status_code = duplicate_username_register_response.status_code

    assert duplicate_username_register_status_code == 400
    
    duplicate_username_register_response_json = duplicate_username_register_response.json()
    assert duplicate_username_register_response_json["detail"] == "Username already exists"

def test_duplicate_email_register(mock_client, user_create_payload):
    # register a user
    original_register_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)

    original_register_status_code = original_register_response.status_code
    assert original_register_status_code == 201

    # attempt to register a user with the same email but different username
    duplicate_email_create_payload = user_create_payload.copy()
    duplicate_email_create_payload["username"] = "new_mock_username"

    duplicate_email_register_response = mock_client.post(USERS_PREFIX + "/register", json=duplicate_email_create_payload)
    duplicate_email_register_status_code = duplicate_email_register_response.status_code

    assert duplicate_email_register_status_code == 400
    
    duplicate_email_register_response_json = duplicate_email_register_response.json()
    assert duplicate_email_register_response_json["detail"] == "Email already registered"

def test_invalid_email_register(mock_client, user_create_payload):
    # register a user with an invalid email format
    incorrect_user_create_payload = user_create_payload.copy()
    incorrect_user_create_payload["email"] = "invalid_mock_email"
    
    invalid_email_register_response = mock_client.post(USERS_PREFIX + "/register", json=incorrect_user_create_payload)

    invalid_email_register_status_code = invalid_email_register_response.status_code
    assert invalid_email_register_status_code == 422

def test_user_list(mock_client, user_create_payload):
    # get list of users when there are no registered users
    empty_get_user_list_response = mock_client.get(USERS_PREFIX + "/")
    
    empty_get_user_list_status_code = empty_get_user_list_response.status_code
    assert empty_get_user_list_status_code == 200

    empty_get_user_list_response_json = empty_get_user_list_response.json()
    assert len(empty_get_user_list_response_json) == 0
    
    # create a first user
    first_user_create_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)
    
    first_user_create_status_code = first_user_create_response.status_code
    assert first_user_create_status_code == 201

    # get list of users after first user registration
    first_get_user_list_response = mock_client.get(USERS_PREFIX + "/")
    
    first_get_user_list_status_code = first_get_user_list_response.status_code
    assert first_get_user_list_status_code == 200

    first_get_user_list_response_json = first_get_user_list_response.json()
    assert len(first_get_user_list_response_json) == 1
    assert first_get_user_list_response_json[0]["username"] == user_create_payload["username"]
    assert first_get_user_list_response_json[0]["email"] == user_create_payload["email"]
    assert first_get_user_list_response_json[0]["id"] == 1

    # create a second user
    new_user_create_payload = user_create_payload.copy()
    new_user_create_payload["username"] = "new_mock_username"
    new_user_create_payload["email"] = "new_mock_email@email.com"

    second_user_create_response = mock_client.post(USERS_PREFIX + "/register", json=new_user_create_payload)
    
    second_user_create_status_code = second_user_create_response.status_code
    assert second_user_create_status_code == 201

    # get list of users after second user registration
    second_get_user_list_response = mock_client.get(USERS_PREFIX + "/")
    
    second_get_user_list_status_code = second_get_user_list_response.status_code
    assert second_get_user_list_status_code == 200
    
    second_get_user_list_response_json = second_get_user_list_response.json()
    assert len(second_get_user_list_response_json) == 2
    assert second_get_user_list_response_json[0]["username"] == user_create_payload["username"]
    assert second_get_user_list_response_json[0]["email"] == user_create_payload["email"]
    assert second_get_user_list_response_json[0]["id"] == 1
    assert second_get_user_list_response_json[1]["username"] == new_user_create_payload["username"]
    assert second_get_user_list_response_json[1]["email"] == new_user_create_payload["email"]
    assert second_get_user_list_response_json[1]["id"] == 2

def test_valid_user_delete(mock_client, user_create_payload):
    # create a user
    user_create_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)
    
    user_create_status_code = user_create_response.status_code
    assert user_create_status_code == 201

    user_id = user_create_response.json()["id"]

    # delete the user
    user_delete_response = mock_client.delete(USERS_PREFIX + f"/{user_id}")

    user_delete_status_code = user_delete_response.status_code
    assert user_delete_status_code == 204

    # check if user is still registered
    get_user_list_response = mock_client.get(USERS_PREFIX + "/")
    
    get_user_list_status_code = get_user_list_response.status_code
    assert get_user_list_status_code == 200

    get_user_list_response_json = get_user_list_response.json()
    assert len(get_user_list_response_json) == 0

def test_invalid_user_delete(mock_client):
    # attempt to delete a user with non-existing user id
    invalid_user_id = 1
    user_delete_response = mock_client.delete(USERS_PREFIX + f"/{invalid_user_id}")

    user_delete_status_code = user_delete_response.status_code
    assert user_delete_status_code == 404

    user_delete_response_json = user_delete_response.json()
    assert user_delete_response_json["detail"] == "User not found"

def test_get_current_user_info(mock_client, user_create_payload, user_login_payload):
    # create a user
    user_create_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)
    
    user_create_status_code = user_create_response.status_code
    assert user_create_status_code == 201

    # get a jwt token
    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=user_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 200

    access_token = get_token_response.json()["access_token"]

    # get current user info
    current_user_info_response = mock_client.get(USERS_PREFIX + "/me", headers={"Authorization":f"Bearer {access_token}"})
    
    current_user_info_status_code = current_user_info_response.status_code
    assert current_user_info_status_code == 200
    
    current_user_info_response_json = current_user_info_response.json()
    assert current_user_info_response_json["username"] == user_create_payload["username"]
    assert current_user_info_response_json["email"] == user_create_payload["email"]

def test_activate_valid_license_key(mock_client_with_admin_tier, user_create_payload, user_login_payload):
    # rename for convenience
    mock_client = mock_client_with_admin_tier
    
    # generate a license key
    generate_license_response = mock_client.post(ADMIN_PREFIX + "/license", json={"quantity" : 1})
    
    generate_license_status_code = generate_license_response.status_code
    assert generate_license_status_code == 201

    generate_license_json = generate_license_response.json()
    license_key = generate_license_json["generated_keys"][0]

    license_key_payload = {
        "key_string" : license_key
    }

    # create a user
    user_create_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)
    
    user_create_status_code = user_create_response.status_code
    assert user_create_status_code == 201

    # check if user created has a free tier
    user_create_json = user_create_response.json()

    assert user_create_json["account_tier"] == "free"
    
    # get jwt token for authentication
    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=user_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 200

    access_token = get_token_response.json()["access_token"]
    authorization_headers = {"Authorization":f"Bearer {access_token}"}    

    # activate license key for user
    activate_license_response = mock_client.post(USERS_PREFIX + "/me/license-activate", json=license_key_payload, headers=authorization_headers)

    activate_license_status_code = activate_license_response.status_code
    assert activate_license_status_code == 200

    activate_license_json = activate_license_response.json()

    assert activate_license_json["detail"] == "License key activated successfully, account upgraded to pro tier"

    # check if user is promoted to pro tier
    current_user_info_response = mock_client.get(USERS_PREFIX + "/me", headers=authorization_headers)
    
    current_user_info_status_code = current_user_info_response.status_code
    assert current_user_info_status_code == 200
    
    current_user_info_response_json = current_user_info_response.json()
    assert current_user_info_response_json["account_tier"] == "pro"

def test_activate_invalid_license_key(mock_client_with_admin_tier, user_create_payload, user_login_payload):
    # rename for convenience
    mock_client = mock_client_with_admin_tier
    
    # generate a license key to ensure valid license keys exist
    generate_license_response = mock_client.post(ADMIN_PREFIX + "/license", json={"quantity" : 1})
    
    generate_license_status_code = generate_license_response.status_code
    assert generate_license_status_code == 201

    license_key_payload = {
        "key_string" : "invalid_mock_license_key"
    }

    # create a user
    user_create_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)
    
    user_create_status_code = user_create_response.status_code
    assert user_create_status_code == 201
    
    # get jwt token for authentication
    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=user_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 200

    access_token = get_token_response.json()["access_token"]
    authorization_headers = {"Authorization":f"Bearer {access_token}"}    

    # activate invalid license key for user
    activate_license_response = mock_client.post(USERS_PREFIX + "/me/license-activate", json=license_key_payload, headers=authorization_headers)

    activate_license_status_code = activate_license_response.status_code
    assert activate_license_status_code == 400

    activate_license_json = activate_license_response.json()

    assert activate_license_json["detail"] == "Invalid or already used license key"

    # check if user is still free tier
    current_user_info_response = mock_client.get(USERS_PREFIX + "/me", headers=authorization_headers)
    
    current_user_info_status_code = current_user_info_response.status_code
    assert current_user_info_status_code == 200
    
    current_user_info_response_json = current_user_info_response.json()
    assert current_user_info_response_json["account_tier"] == "free"

def test_activate_used_license_key(mock_client_with_admin_tier, user_create_payload, user_login_payload):
    # rename for convenience
    mock_client = mock_client_with_admin_tier
    
    # generate a license key to ensure valid license keys exist
    generate_license_response = mock_client.post(ADMIN_PREFIX + "/license", json={"quantity" : 1})
    
    generate_license_status_code = generate_license_response.status_code
    assert generate_license_status_code == 201

    generate_license_json = generate_license_response.json()
    license_key = generate_license_json["generated_keys"][0]

    license_key_payload = {
        "key_string" : license_key
    }
    
    # create the first user
    user_create_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)
    
    user_create_status_code = user_create_response.status_code
    assert user_create_status_code == 201

    # get jwt token for authentication for the first user
    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=user_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 200

    access_token = get_token_response.json()["access_token"]
    authorization_headers = {"Authorization":f"Bearer {access_token}"}    

    # activate license key for first user
    activate_license_response = mock_client.post(USERS_PREFIX + "/me/license-activate", json=license_key_payload, headers=authorization_headers)

    activate_license_status_code = activate_license_response.status_code
    assert activate_license_status_code == 200

    # create a second user
    new_user_create_payload = user_create_payload.copy()
    new_user_create_payload["username"] = "new_mock_username"
    new_user_create_payload["email"] = "new_mock_email@email.com"

    second_user_create_response = mock_client.post(USERS_PREFIX + "/register", json=new_user_create_payload)
    
    second_user_create_status_code = second_user_create_response.status_code
    assert second_user_create_status_code == 201

   # get jwt token for authentication for the second user
    new_user_login_payload = user_create_payload.copy()
    new_user_login_payload["username"] = "new_mock_email@email.com"

    get_new_token_response = mock_client.post(AUTH_PREFIX + "/token", data=new_user_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_new_token_status_code = get_new_token_response.status_code    
    assert get_new_token_status_code == 200

    new_access_token = get_new_token_response.json()["access_token"]
    new_authorization_headers = {"Authorization":f"Bearer {new_access_token}"}    

    # activate license key for second user
    new_activate_license_response = mock_client.post(USERS_PREFIX + "/me/license-activate", json=license_key_payload, headers=new_authorization_headers)

    new_activate_license_status_code = new_activate_license_response.status_code
    assert new_activate_license_status_code == 400

    new_activate_license_json = new_activate_license_response.json()

    assert new_activate_license_json["detail"] == "Invalid or already used license key"

    # check if second user is still free tier
    current_user_info_response = mock_client.get(USERS_PREFIX + "/me", headers=new_authorization_headers)
    
    current_user_info_status_code = current_user_info_response.status_code
    assert current_user_info_status_code == 200
    
    current_user_info_response_json = current_user_info_response.json()
    assert current_user_info_response_json["account_tier"] == "free"

def test_activate_license_key_for_pro_user(mock_client_with_admin_tier, user_create_payload, user_login_payload):
    # rename for convenience
    mock_client = mock_client_with_admin_tier
    
    # generate license keys
    generate_license_response = mock_client.post(ADMIN_PREFIX + "/license", json={"quantity" : 2})
    
    generate_license_status_code = generate_license_response.status_code
    assert generate_license_status_code == 201

    generate_license_json = generate_license_response.json()
    license_key1 = generate_license_json["generated_keys"][0]
    license_key2 = generate_license_json["generated_keys"][1]

    license_key_payload1 = {
        "key_string" : license_key1
    }

    license_key_payload2 = {
        "key_string" : license_key2
    }

    # create a user
    user_create_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)
    
    user_create_status_code = user_create_response.status_code
    assert user_create_status_code == 201

    # check if user created has a free tier
    user_create_json = user_create_response.json()

    assert user_create_json["account_tier"] == "free"
    
    # get jwt token for authentication
    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=user_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 200

    access_token = get_token_response.json()["access_token"]
    authorization_headers = {"Authorization":f"Bearer {access_token}"}    

    # activate license key for user
    activate_license_response1 = mock_client.post(USERS_PREFIX + "/me/license-activate", json=license_key_payload1, headers=authorization_headers)

    activate_license_status_code1 = activate_license_response1.status_code
    assert activate_license_status_code1 == 200

    # check if user is promoted to pro tier
    current_user_info_response = mock_client.get(USERS_PREFIX + "/me", headers=authorization_headers)
    
    current_user_info_status_code = current_user_info_response.status_code
    assert current_user_info_status_code == 200
    
    current_user_info_response_json = current_user_info_response.json()
    assert current_user_info_response_json["account_tier"] == "pro"

    # activate another license key for user
    activate_license_response2 = mock_client.post(USERS_PREFIX + "/me/license-activate", json=license_key_payload2, headers=authorization_headers)

    activate_license_status_code2 = activate_license_response2.status_code
    assert activate_license_status_code2 == 400

    activate_license_json2 = activate_license_response2.json()
    assert activate_license_json2["detail"] == "Account already upgraded to pro tier"