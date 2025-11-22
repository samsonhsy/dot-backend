# tests/test_users.py
import utils

USERS_PREFIX = "/users"
AUTH_PREFIX = "/auth"

# token authentication tests
def test_invalid_token_authentication(mock_client):
    """
    Verifies that the api rejects attempts to access user-specific information without authentication
    """
    # attempt to authenticate with invalid token
    invalid_access_token = "invalid_access_token"
    authorization_headers = utils.get_authorization_headers(invalid_access_token)

    current_user_info_response = mock_client.get(USERS_PREFIX + "/me", headers=authorization_headers)
    
    current_user_info_status_code = current_user_info_response.status_code
    assert current_user_info_status_code == 401

    current_user_info_json = current_user_info_response.json()
    assert current_user_info_json["detail"] == "Could not validate credentials"

# user login tests
def test_valid_login(mock_client, user_create_payload):
    """
    Verifies that the api properly returns a token for authentication after user login 
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # login for jwt token
    user_login_payload = utils.get_user_login_payload(user_create_payload)

    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=user_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 200

    token_type = get_token_response.json()["token_type"]
    assert token_type == "bearer"

    access_token = get_token_response.json()["access_token"]

    # check if token is valid
    authorization_headers = utils.get_authorization_headers(access_token)
    current_user_info_response = mock_client.get(USERS_PREFIX + "/me", headers=authorization_headers)
    
    current_user_info_status_code = current_user_info_response.status_code
    assert current_user_info_status_code == 200
    
    current_user_info_json = current_user_info_response.json()
    assert current_user_info_json["email"] == user_create_payload["email"]

def test_invalid_username_login(mock_client, user_create_payload):
    """
    Verifies that the api rejects attempts to login with non-existant username
    """
    # login for jwt token with invalid username
    user_login_payload = utils.get_user_login_payload(user_create_payload)

    invaid_username_login_payload = user_login_payload.copy()
    invaid_username_login_payload["username"] = "invalid_mock_username"

    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=invaid_username_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 401

    get_token_json = get_token_response.json()
    assert get_token_json["detail"] == "Incorrect email or password"

def test_invalid_password_login(mock_client, user_create_payload):
    """
    Verifies that the api rejects attempts to login with an incorrect password
    """
    # login for jwt token with invalid password
    user_login_payload = utils.get_user_login_payload(user_create_payload)

    invalid_password_login_payload = user_login_payload.copy()
    invalid_password_login_payload["password"] = "invalid_mock_password"

    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=invalid_password_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 401

    get_token_json = get_token_response.json()
    assert get_token_json["detail"] == "Incorrect email or password"

