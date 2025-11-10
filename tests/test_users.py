# tests/test_users.py
PREFIX = "/users"

def test_valid_register(mock_client, user_create_payload):
    response = mock_client.post(PREFIX + "/register", json=user_create_payload)
    
    status_code = response.status_code    
    assert status_code == 201

    response_json = response.json()

    assert response_json["username"] == user_create_payload["username"]
    assert response_json["email"] == user_create_payload["email"]
    assert response_json["id"] == 1

def test_duplicate_username_register(mock_client, user_create_payload):
    original_register_response = mock_client.post(PREFIX + "/register", json=user_create_payload)

    original_register_status_code = original_register_response.status_code
    assert original_register_status_code == 201

    duplicate_username_create_payload = user_create_payload.copy()
    duplicate_username_create_payload["email"] = "new_mock_email@email.com"

    duplicate_username_register_response = mock_client.post(PREFIX + "/register", json=duplicate_username_create_payload)
    duplicate_username_register_status_code = duplicate_username_register_response.status_code

    assert duplicate_username_register_status_code == 400
    
    duplicate_username_register_response_json = duplicate_username_register_response.json()
    assert duplicate_username_register_response_json["detail"] == "Username already exists"

def test_duplicate_email_register(mock_client, user_create_payload):
    original_register_response = mock_client.post(PREFIX + "/register", json=user_create_payload)

    original_register_status_code = original_register_response.status_code
    assert original_register_status_code == 201

    duplicate_email_create_payload = user_create_payload.copy()
    duplicate_email_create_payload["username"] = "new_mock_username"

    duplicate_email_register_response = mock_client.post(PREFIX + "/register", json=duplicate_email_create_payload)
    duplicate_email_register_status_code = duplicate_email_register_response.status_code

    assert duplicate_email_register_status_code == 400
    
    duplicate_email_register_response_json = duplicate_email_register_response.json()
    assert duplicate_email_register_response_json["detail"] == "Email already registered"

def test_invalid_email_register(mock_client, user_create_payload):
    incorrect_user_create_payload = user_create_payload.copy()
    incorrect_user_create_payload["email"] = "invalid_mock_email"
    
    invalid_email_register_response = mock_client.post(PREFIX + "/register", json=incorrect_user_create_payload)

    invalid_email_register_status_code = invalid_email_register_response.status_code
    assert invalid_email_register_status_code == 422

