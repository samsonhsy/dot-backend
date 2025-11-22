# tests/test_users.py
import pytest
import utils

USERS_PREFIX = "/users"
AUTH_PREFIX = "/auth"
ADMIN_PREFIX = "/admin"

# user registration tests
def test_valid_register(mock_client, user_create_payload):
    """
    Verifies that the api properly registers a user
    """
    # create the user
    user_create_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)
    
    user_create_status_code = user_create_response.status_code    
    assert user_create_status_code == 201

    user_create_json = user_create_response.json()

    assert user_create_json["username"] == user_create_payload["username"]
    assert user_create_json["email"] == user_create_payload["email"]
    assert user_create_json["id"] == 1

    # check if user exists in database after registration
    get_user_list_response_json = utils.get_user_list(mock_client)

    assert get_user_list_response_json[0]["username"] == user_create_payload["username"]
    assert get_user_list_response_json[0]["email"] == user_create_payload["email"]
    assert get_user_list_response_json[0]["id"] == 1

def test_duplicate_username_register(mock_client, user_create_payload):
    """
    Verifies that the api rejects user registration attempts that include an already existing username
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # attempt to register a user with the same username but different email
    duplicate_username_create_payload = user_create_payload.copy()
    duplicate_username_create_payload["email"] = "new_mock_email@email.com"

    duplicate_username_register_response = mock_client.post(USERS_PREFIX + "/register", json=duplicate_username_create_payload)
    duplicate_username_register_status_code = duplicate_username_register_response.status_code

    assert duplicate_username_register_status_code == 400
    
    duplicate_username_register_response_json = duplicate_username_register_response.json()
    assert duplicate_username_register_response_json["detail"] == "Username already exists"

def test_duplicate_email_register(mock_client, user_create_payload):
    """
    Verifies that the api rejects user registration attempts that include an already registered email
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # attempt to register a user with the same email but different username
    duplicate_email_create_payload = user_create_payload.copy()
    duplicate_email_create_payload["username"] = "new_mock_username"

    duplicate_email_register_response = mock_client.post(USERS_PREFIX + "/register", json=duplicate_email_create_payload)
    duplicate_email_register_status_code = duplicate_email_register_response.status_code

    assert duplicate_email_register_status_code == 400
    
    duplicate_email_register_response_json = duplicate_email_register_response.json()
    assert duplicate_email_register_response_json["detail"] == "Email already registered"

def test_invalid_email_register(mock_client, user_create_payload):
    """
    Verifies that the api rejects user registration attempts that include an invalid email format
    """
    # register a user with an invalid email format
    incorrect_user_create_payload = user_create_payload.copy()
    incorrect_user_create_payload["email"] = "invalid_mock_email"
    
    invalid_email_register_response = mock_client.post(USERS_PREFIX + "/register", json=incorrect_user_create_payload)

    invalid_email_register_status_code = invalid_email_register_response.status_code
    assert invalid_email_register_status_code == 422

# user listing tests
def test_user_list(mock_client, user_create_payload):
    """
    Verifies that the api returns a list of all registered users
    """
    # get list of users when there are no registered users
    get_user_list_response_0 = mock_client.get(USERS_PREFIX + "/")
    
    get_user_list_status_code_0 = get_user_list_response_0.status_code
    assert get_user_list_status_code_0 == 200

    get_user_list_json_0 = get_user_list_response_0.json()
    assert len(get_user_list_json_0) == 0
    
    # create a first user
    utils.create_new_user(mock_client, user_create_payload)

    # get list of users after first user registration
    get_user_list_response_1 = mock_client.get(USERS_PREFIX + "/")
    
    get_user_list_status_code_1 = get_user_list_response_1.status_code
    assert get_user_list_status_code_1 == 200

    get_user_list_json_1 = get_user_list_response_1.json()
    assert len(get_user_list_json_1) == 1
    assert get_user_list_json_1[0]["username"] == user_create_payload["username"]
    assert get_user_list_json_1[0]["email"] == user_create_payload["email"]
    assert get_user_list_json_1[0]["id"] == 1

    # create a second user
    user_create_payload_2 = user_create_payload.copy()
    user_create_payload_2["username"] = "new_mock_username"
    user_create_payload_2["email"] = "new_mock_email@email.com"

    utils.create_new_user(mock_client, user_create_payload_2)

    # get list of users after second user registration
    get_user_list_response_2 = mock_client.get(USERS_PREFIX + "/")
    
    get_user_list_status_code_2 = get_user_list_response_2.status_code
    assert get_user_list_status_code_2 == 200
    
    second_get_user_list_json_2 = get_user_list_response_2.json()
    assert len(second_get_user_list_json_2) == 2
    
    assert second_get_user_list_json_2[0]["username"] == user_create_payload["username"]
    assert second_get_user_list_json_2[0]["email"] == user_create_payload["email"]
    assert second_get_user_list_json_2[0]["id"] == 1

    assert second_get_user_list_json_2[1]["username"] == user_create_payload_2["username"]
    assert second_get_user_list_json_2[1]["email"] == user_create_payload_2["email"]
    assert second_get_user_list_json_2[1]["id"] == 2

# user deletion tests
def test_valid_user_delete(mock_client, user_create_payload):
    """
    Verifies that the api properly deletes a user
    """
    # create a user
    user_create_json = utils.create_new_user(mock_client, user_create_payload)

    # delete the user
    user_id = user_create_json["id"]
    user_delete_response = mock_client.delete(USERS_PREFIX + f"/{user_id}")

    user_delete_status_code = user_delete_response.status_code
    assert user_delete_status_code == 204

    # check if user is still registered
    get_user_list_json = utils.get_user_list(mock_client)
    assert len(get_user_list_json) == 0

def test_invalid_user_delete(mock_client):
    """
    Verifies that the api rejects attempts to delete non-existant users
    """
    # attempt to delete a user with non-existing user id
    invalid_user_id = 1
    user_delete_response = mock_client.delete(USERS_PREFIX + f"/{invalid_user_id}")

    user_delete_status_code = user_delete_response.status_code
    assert user_delete_status_code == 404

    user_delete_json = user_delete_response.json()
    assert user_delete_json["detail"] == "User not found"

# user information retrival tests
def test_get_current_user_info(mock_client, user_create_payload):
    """
    Verifies that the api returns the information of the user sending the request
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)

    # get current user info
    authorization_headers = utils.get_authorization_headers(access_token)
    current_user_info_response = mock_client.get(USERS_PREFIX + "/me", headers=authorization_headers)
    
    current_user_info_status_code = current_user_info_response.status_code
    assert current_user_info_status_code == 200
    
    current_user_info_json = current_user_info_response.json()
    assert current_user_info_json["username"] == user_create_payload["username"]
    assert current_user_info_json["email"] == user_create_payload["email"]

# user license activation tests
def test_activate_valid_license_key(mock_client_with_admin_tier, user_create_payload):
    """
    Verifies that the api can properly activate a license key for a user
    """
    # rename for convenience
    mock_client = mock_client_with_admin_tier
    
    # generate a license key
    generate_license_json = utils.generate_license_keys(mock_client, 1)
    license_key = generate_license_json["generated_keys"][0]

    license_key_payload = utils.get_license_key_payload(license_key)

    # create a user
    user_create_json = utils.create_new_user(mock_client, user_create_payload)

    # check if user created has a free tier
    assert user_create_json["account_tier"] == "free"
    
    # get jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)

    # activate license key for user
    authorization_headers = utils.get_authorization_headers(access_token) 
    activate_license_response = mock_client.post(USERS_PREFIX + "/me/license-activate", json=license_key_payload, headers=authorization_headers)

    activate_license_status_code = activate_license_response.status_code
    assert activate_license_status_code == 200

    activate_license_json = activate_license_response.json()

    assert activate_license_json["detail"] == "License key activated successfully, account upgraded to pro tier"

    # check if user is promoted to pro tier
    current_user_info_json = utils.get_user_list(mock_client)[0]
    assert current_user_info_json["account_tier"] == "pro"

def test_activate_invalid_license_key(mock_client_with_admin_tier, user_create_payload):
    """
    Verifies that the api rejects attempts to activate non-existant license keys
    """
    # rename for convenience
    mock_client = mock_client_with_admin_tier
    
    # generate a license key to ensure valid license keys exist
    generate_license_json = utils.generate_license_keys(mock_client, 1)
    license_key = generate_license_json["generated_keys"][0]
    
    invalid_license_key = "#$#$#%$%@@#"

    license_key_payload = utils.get_license_key_payload(invalid_license_key)

    # create a user
    utils.create_new_user(mock_client, user_create_payload)
    
    # get jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)

    # activate invalid license key for user
    authorization_headers = utils.get_authorization_headers(access_token)
    activate_license_response = mock_client.post(USERS_PREFIX + "/me/license-activate", json=license_key_payload, headers=authorization_headers)

    activate_license_status_code = activate_license_response.status_code
    assert activate_license_status_code == 400

    activate_license_json = activate_license_response.json()

    assert activate_license_json["detail"] == "Invalid or already used license key"

    # check if user is still free tier
    current_user_info_json = utils.get_user_list(mock_client)[0]
    assert current_user_info_json["account_tier"] == "free"

def test_activate_used_license_key(mock_client_with_admin_tier, user_create_payload):
    """
    Verifies that the api rejects attempts to activate already used license keys
    """
    # rename for convenience
    mock_client = mock_client_with_admin_tier
    
    # generate a license key to ensure valid license keys exist
    generate_license_json = utils.generate_license_keys(mock_client, 1)
    license_key = generate_license_json["generated_keys"][0]

    license_key_payload = utils.get_license_key_payload(license_key)

    # create a user
    utils.create_new_user(mock_client, user_create_payload)
    
    # get jwt token for authentication
    user_login_payload_1 = utils.get_user_login_payload(user_create_payload)
    access_token_1 = utils.get_user_access_token(mock_client, user_login_payload_1)

    # activate license key for first user
    authorization_headers_1 = utils.get_authorization_headers(access_token_1)
    activate_license_response_1 = mock_client.post(USERS_PREFIX + "/me/license-activate", json=license_key_payload, headers=authorization_headers_1)

    activate_license_status_code_1 = activate_license_response_1.status_code
    assert activate_license_status_code_1 == 200

    # create a second user
    user_create_payload_2 = user_create_payload.copy()
    user_create_payload_2["username"] = "new_mock_username"
    user_create_payload_2["email"] = "new_mock_email@email.com"

    utils.create_new_user(mock_client, user_create_payload_2)

   # get jwt token for authentication for the second user
    user_login_payload_2 = utils.get_user_login_payload(user_create_payload_2)
    access_token_2 = utils.get_user_access_token(mock_client, user_login_payload_2)

    authorization_headers_2 = utils.get_authorization_headers(access_token_2)   

    # activate license key for second user
    activate_license_response_2 = mock_client.post(USERS_PREFIX + "/me/license-activate", json=license_key_payload, headers=authorization_headers_2)

    activate_license_status_code_2 = activate_license_response_2.status_code
    assert activate_license_status_code_2 == 400

    activate_license_json_2 = activate_license_response_2.json()

    assert activate_license_json_2["detail"] == "Invalid or already used license key"

    # check if second user is still free tier
    second_user_info_json = utils.get_user_list(mock_client)[1]
    assert second_user_info_json["account_tier"] == "free"

@pytest.mark.parametrize("user_tier, expected_message", [
    ("pro", "Account already upgraded to pro tier"),
    ("admin", "Admin accounts don't need upgrade")])
def test_activate_license_key_for_nonfree_user(mock_client_with_admin_tier, user_create_payload, user_tier, expected_message):
    """
    Verifies that the api rejects attempts to activate license keys by non-free users
    """
    # rename for convenience
    mock_client = mock_client_with_admin_tier
    
    # generate license keys
    generate_license_json = utils.generate_license_keys(mock_client, 1)
    
    license_key = generate_license_json["generated_keys"][0]
    license_key_payload = utils.get_license_key_payload(license_key)

    # create a user
    user_create_json = utils.create_new_user(mock_client, user_create_payload)
    user_id = user_create_json["id"]

    # get jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # promote user to pro
    utils.promote_user(mock_client, user_id, user_tier)

    # activate license key for user
    activate_license_response = mock_client.post(USERS_PREFIX + "/me/license-activate", json=license_key_payload, headers=authorization_headers)

    activate_license_status_code = activate_license_response.status_code
    assert activate_license_status_code == 400

    activate_license_json = activate_license_response.json()
    assert activate_license_json["detail"] == expected_message

