# tests/helpers/utils.py
USERS_PREFIX = "/users"
AUTH_PREFIX = "/auth"
ADMIN_PREFIX = "/admin"

def create_new_user(mock_client, user_create_payload):
    user_create_response = mock_client.post(USERS_PREFIX + "/register", json=user_create_payload)
    
    user_create_status_code = user_create_response.status_code    
    assert user_create_status_code == 201

    user_create_json = user_create_response.json()

    return user_create_json

def get_user_list(mock_client):
    get_user_list_response = mock_client.get(USERS_PREFIX + "/")
    
    get_user_list_status_code = get_user_list_response.status_code
    assert get_user_list_status_code == 200

    get_user_list_json = get_user_list_response.json()

    return get_user_list_json

def get_user_access_token(mock_client, user_login_payload):
    get_token_response = mock_client.post(AUTH_PREFIX + "/token", data=user_login_payload, headers={"content-type": "application/x-www-form-urlencoded"})
    
    get_token_status_code = get_token_response.status_code    
    assert get_token_status_code == 200

    access_token = get_token_response.json()["access_token"]

    return access_token

def get_authorization_headers(access_token):
    authorization_headers = {"Authorization":f"Bearer {access_token}"}

    return authorization_headers

def get_user_login_payload(user_create_payload):
    return {
        "username": user_create_payload["email"],
        "password": user_create_payload["password"]
    }

def generate_license_keys(mock_client, quantity):
    generate_license_response = mock_client.post(ADMIN_PREFIX + "/license", json={"quantity" : quantity})
    
    generate_license_status_code = generate_license_response.status_code
    assert generate_license_status_code == 201

    generate_license_json = generate_license_response.json()

    return generate_license_json

def get_license_key_payload(license_key):
    return {
        "key_string" : license_key
    }