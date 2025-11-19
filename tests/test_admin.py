# tests/test_admin.py
import utils
import pytest

ADMIN_PREFIX = "/admin"

PROMOTE_USER_PARAMETERS = ["pro", "admin"]

def test_create_license_keys(mock_client_with_admin_tier, key_generation_request):
    # rename for convenience
    mock_client = mock_client_with_admin_tier

    # generate license keys
    generate_license_response = mock_client.post(ADMIN_PREFIX + "/license", json=key_generation_request)

    generate_license_status_code = generate_license_response.status_code
    assert generate_license_status_code == 201

    generate_license_json = generate_license_response.json()
    generated_keys = generate_license_json["generated_keys"]
    
    assert len(generated_keys) == key_generation_request["quantity"] 

@pytest.mark.parametrize("target_tier", PROMOTE_USER_PARAMETERS)
def test_valid_promote_user(mock_client_with_admin_tier, user_create_payload, target_tier):
    # rename for convenience
    mock_client = mock_client_with_admin_tier

    # create a user
    user_create_json = utils.create_new_user(mock_client, user_create_payload)
    user_id = user_create_json["id"]
    username = user_create_json["username"]

    # check the tier of the user
    current_user_info_json_1 = utils.get_user_list(mock_client)[0]
    assert current_user_info_json_1["account_tier"] == "free"

    # promote the user
    user_promote_request = {
        "user_id": user_id,
        "to_tier": target_tier
    }

    user_promote_response = mock_client.post(ADMIN_PREFIX + "/promote-user", json=user_promote_request)
    
    user_promote_status_code = user_promote_response.status_code
    assert user_promote_status_code == 200

    user_promote_json = user_promote_response.json()
    assert user_promote_json["detail"] == f"User {username} promoted to {target_tier} tier successfully"
    assert user_promote_json["user_id"] == user_id
    assert user_promote_json["username"] == username
    assert user_promote_json["new_tier"] == target_tier

    # check the tier of the user after promotion
    current_user_info_json_2 = utils.get_user_list(mock_client)[0]
    assert current_user_info_json_2["account_tier"] == target_tier
    
@pytest.mark.parametrize("target_tier", PROMOTE_USER_PARAMETERS)
def test_promote_user_to_same_tier(mock_client_with_admin_tier, user_create_payload, target_tier):
    # rename for convenience
    mock_client = mock_client_with_admin_tier

    # create a user
    user_create_json = utils.create_new_user(mock_client, user_create_payload)
    user_id = user_create_json["id"]
    username = user_create_json["username"]

    # check the tier of the user
    current_user_info_json_1 = utils.get_user_list(mock_client)[0]
    assert current_user_info_json_1["account_tier"] == "free"

    # promote the user
    user_promote_request = {
        "user_id": user_id,
        "to_tier": target_tier
    }

    user_promote_response_1 = mock_client.post(ADMIN_PREFIX + "/promote-user", json=user_promote_request)
    
    user_promote_status_code_1 = user_promote_response_1.status_code
    assert user_promote_status_code_1 == 200

    # check the tier of the user after promotion
    current_user_info_json_2 = utils.get_user_list(mock_client)[0]
    assert current_user_info_json_2["account_tier"] == target_tier

    # attempt to promote the user to the same tier 
    user_promote_response_2 = mock_client.post(ADMIN_PREFIX + "/promote-user", json=user_promote_request)
    
    user_promote_status_code_2 = user_promote_response_2.status_code
    assert user_promote_status_code_2 == 400 

    user_promote_json_2 = user_promote_response_2.json()

    assert user_promote_json_2["detail"] == f"User {username} is already in {target_tier} tier"

def test_promote_user_to_unknown_tier(mock_client_with_admin_tier, user_create_payload):
    # rename for convenience
    mock_client = mock_client_with_admin_tier

    # create a user
    user_create_json = utils.create_new_user(mock_client, user_create_payload)
    user_id = user_create_json["id"]
    username = user_create_json["username"]

    # promote the user
    user_promote_request = {
        "user_id": user_id,
        "to_tier": "invalid_tier_name"
    }

    user_promote_response_1 = mock_client.post(ADMIN_PREFIX + "/promote-user", json=user_promote_request)
    
    user_promote_status_code_1 = user_promote_response_1.status_code
    assert user_promote_status_code_1 == 422

@pytest.mark.parametrize("target_tier", PROMOTE_USER_PARAMETERS)
def test_promote_unknown_user(mock_client_with_admin_tier, target_tier):
    # rename for convenience
    mock_client = mock_client_with_admin_tier

    # create invalid user id
    invalid_user_id = 1

    # promote the user
    user_promote_request = {
        "user_id": invalid_user_id,
        "to_tier": target_tier
    }

    user_promote_response = mock_client.post(ADMIN_PREFIX + "/promote-user", json=user_promote_request)
    
    user_promote_status_code = user_promote_response.status_code
    assert user_promote_status_code == 404

    user_promote_json = user_promote_response.json()
    assert user_promote_json["detail"] == "User not found"

def test_insufficient_privileges(mock_client, user_create_payload, key_generation_request):
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)

    # attempt to generate license keys with insufficient privileges
    authorization_headers = utils.get_authorization_headers(access_token)
    
    generate_license_response = mock_client.post(ADMIN_PREFIX + "/license", json=key_generation_request, headers=authorization_headers)

    generate_license_status_code = generate_license_response.status_code
    assert generate_license_status_code == 403

    generate_license_json = generate_license_response.json()
    assert generate_license_json["detail"] == "Insufficient privileges"