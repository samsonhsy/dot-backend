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

def test_user_list(mock_client, user_create_payload):
    # get list of users when there are no registered users
    empty_get_user_list_response = mock_client.get(PREFIX + "/")
    
    empty_get_user_list_status_code = empty_get_user_list_response.status_code
    assert empty_get_user_list_status_code == 200

    empty_get_user_list_response_json = empty_get_user_list_response.json()
    assert len(empty_get_user_list_response_json) == 0
    
    # create a first user
    first_user_create_response = mock_client.post(PREFIX + "/register", json=user_create_payload)
    
    first_user_create_status_code = first_user_create_response.status_code
    assert first_user_create_status_code == 201

    # get list of users after first user registration
    first_get_user_list_response = mock_client.get(PREFIX + "/")
    
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

    second_user_create_response = mock_client.post(PREFIX + "/register", json=new_user_create_payload)
    
    second_user_create_status_code = second_user_create_response.status_code
    assert second_user_create_status_code == 201

    # get list of users after second user registration
    second_get_user_list_response = mock_client.get(PREFIX + "/")
    
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

def test_user_delete(mock_client, user_create_payload):
    # create a user
    user_create_response = mock_client.post(PREFIX + "/register", json=user_create_payload)
    
    user_create_status_code = user_create_response.status_code
    assert user_create_status_code == 201

    user_id = user_create_response.json()["id"]

    # delete the user
    user_delete_response = mock_client.delete(PREFIX + f"/{user_id}")

    user_delete_status_code = user_delete_response.status_code
    assert user_delete_status_code == 200

    # check if user is still registered
    get_user_list_response = mock_client.get(PREFIX + "/")
    
    get_user_list_status_code = get_user_list_response.status_code
    assert get_user_list_status_code == 200

    get_user_list_response_json = get_user_list_response.json()
    assert len(get_user_list_response_json) == 0