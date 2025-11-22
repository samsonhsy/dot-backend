# tests/test_admin.py
import utils
import pytest

ADMIN_PREFIX = "/admin"

USER_TIER_PARAMETERS = ["pro", "admin"]

# insufficient privileges tests
def test_admin_endpoint_with_insufficient_privileges(mock_client, user_create_payload, key_generation_request):
    """
    Verifies that the api rejects attempts to generate license keys by non-admin users
    """
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

# license creation tests
def test_create_license_keys(mock_client_with_admin_tier, key_generation_request):
    """
    Verifies that the api can properly generate license keys
    """
    # rename for convenience
    mock_client = mock_client_with_admin_tier

    # generate license keys
    generate_license_response = mock_client.post(ADMIN_PREFIX + "/license", json=key_generation_request)

    generate_license_status_code = generate_license_response.status_code
    assert generate_license_status_code == 201

    generate_license_json = generate_license_response.json()
    generated_keys = generate_license_json["generated_keys"]
    
    assert len(generated_keys) == key_generation_request["quantity"] 

# license listing tests
def test_list_license_keys(mock_client_with_admin_tier, key_generation_request):
    """
    Verifies that the api returns a list of all license keys in the database
    """
    # rename for convenience
    mock_client = mock_client_with_admin_tier

    # generate license keys
    key_quantity = key_generation_request["quantity"]
    generate_license_json = utils.generate_license_keys(mock_client, key_quantity)

    generated_keys = generate_license_json["generated_keys"]

    # get a list of license keys
    list_license_keys_response = mock_client.get(ADMIN_PREFIX + "/license")

    list_license_keys_status_code = list_license_keys_response.status_code
    assert list_license_keys_status_code == 200

    list_license_keys_json = list_license_keys_response.json()

    listed_keys = [license_key["key_string"] for license_key in list_license_keys_json]

    assert len(list_license_keys_json) == len(generated_keys)
    assert listed_keys == generated_keys

# license deletion tests
def test_valid_delete_license_key(mock_client_with_admin_tier, key_generation_request):
    """
    Verifies that the api can properly delete a license key from the database
    """
    # rename for convenience
    mock_client = mock_client_with_admin_tier

    # generate license keys
    key_quantity = key_generation_request["quantity"]
    generate_license_json = utils.generate_license_keys(mock_client, key_quantity)

    generated_keys = generate_license_json["generated_keys"]

    # check the number of license keys before deletion
    list_license_keys_json_0 = utils.list_license_keys(mock_client)

    assert len(list_license_keys_json_0) == key_quantity

    # delete the a license key
    del generated_keys[0]
    expected_listed_keys = generated_keys

    key_id = list_license_keys_json_0[0]["id"]

    delete_license_key_repsonse = mock_client.delete(ADMIN_PREFIX + f"/license/{key_id}")

    delete_license_key_status_code = delete_license_key_repsonse.status_code
    assert delete_license_key_status_code == 204

    # check if license key has been deleted
    list_license_keys_json_1 = utils.list_license_keys(mock_client)
    listed_keys = [license_key["key_string"] for license_key in list_license_keys_json_1]

    assert len(list_license_keys_json_1) == key_quantity - 1
    assert listed_keys == expected_listed_keys

def test_delete_invalid_license_key(mock_client_with_admin_tier):
    """
    Verifies that the api rejects attempts to delete non-existant license keys
    """
    # rename for convenience
    mock_client = mock_client_with_admin_tier

    # attempt to delete an invalid license key
    invalid_key_id = 0

    delete_license_key_repsonse = mock_client.delete(ADMIN_PREFIX + f"/license/{invalid_key_id}")

    delete_license_key_status_code = delete_license_key_repsonse.status_code
    assert delete_license_key_status_code == 404

    delete_license_key_json = delete_license_key_repsonse.json()

    assert delete_license_key_json["detail"] == "License key not found"

# user promotion tests
@pytest.mark.parametrize("target_tier", USER_TIER_PARAMETERS)
def test_valid_promote_user(mock_client_with_admin_tier, user_create_payload, target_tier):
    """
    Verifies that the api can properly promote a user to a higher tier
    """
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
    
@pytest.mark.parametrize("target_tier", USER_TIER_PARAMETERS)
def test_promote_user_to_same_tier(mock_client_with_admin_tier, user_create_payload, target_tier):
    """
    Verifies that the api rejects attempts to promote a user to the same tier as the user
    """
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

def test_promote_user_to_invalid_tier(mock_client_with_admin_tier, user_create_payload):
    """
    Verifies that the api rejects attempts to promote users to a non-existant tier
    """
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

@pytest.mark.parametrize("target_tier", USER_TIER_PARAMETERS)
def test_promote_invalid_user(mock_client_with_admin_tier, target_tier):
    """
    Verifies that the api rejects attempts to promote non-existant users
    """
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

