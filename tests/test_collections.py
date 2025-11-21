# tests/test_collections.py
import pytest
import utils
import json

import io
import zipfile

from app.services.dotfile_service import generate_dotfile_name_in_collection 
from app.core.settings import settings

COLLECTIONS_PREFIX = "/collections"

FILE_INDICES = [0, 1]

FREE_TIER_RETRIEVAL_LIMIT = settings.FREE_TIER_RETRIEVAL_LIMIT

def test_create_collection(mock_client, user_create_payload, collection_create_payload):
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)

    # create collection
    authorization_headers = utils.get_authorization_headers(access_token)
    collection_create_response = mock_client.post(COLLECTIONS_PREFIX + "/", json=collection_create_payload, headers=authorization_headers)

    collection_create_status_code = collection_create_response.status_code
    assert collection_create_status_code == 201

    collection_create_json = collection_create_response.json()

    assert collection_create_json["id"] == 1
    assert collection_create_json["name"] == collection_create_payload["name"]
    assert collection_create_json["description"] == collection_create_payload["description"]

def test_get_my_collections(mock_client, user_create_payload, collection_create_payload):
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # get empty list of collection
    get_collection_list_response_0 = mock_client.get(COLLECTIONS_PREFIX + "/owned", headers=authorization_headers)

    get_collection_list_status_code_0 = get_collection_list_response_0.status_code
    assert get_collection_list_status_code_0 == 200

    get_collection_list_json_0 = get_collection_list_response_0.json()
    assert len(get_collection_list_json_0) == 0

    # create a first collection
    utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)

    # get list of collection with one collection
    get_collection_list_response_1 = mock_client.get(COLLECTIONS_PREFIX + "/owned", headers=authorization_headers)

    get_collection_list_status_code_1 = get_collection_list_response_1.status_code
    assert get_collection_list_status_code_1 == 200

    get_collection_list_json_1 = get_collection_list_response_1.json()
    assert len(get_collection_list_json_1) == 1
    assert get_collection_list_json_1[0]["id"] == 1
    assert get_collection_list_json_1[0]["name"] == collection_create_payload["name"]
    assert get_collection_list_json_1[0]["description"] == collection_create_payload["description"]

    # create a second collection
    utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)

    # get list of collection with two collection
    get_collection_list_response_2 = mock_client.get(COLLECTIONS_PREFIX + "/owned", headers=authorization_headers)

    get_collection_list_status_code_2 = get_collection_list_response_2.status_code
    assert get_collection_list_status_code_2 == 200

    get_collection_list_json_2 = get_collection_list_response_2.json()
    assert len(get_collection_list_json_2) == 2
    assert get_collection_list_json_2[1]["id"] == 2
    assert get_collection_list_json_2[1]["name"] == collection_create_payload["name"]
    assert get_collection_list_json_2[1]["description"] == collection_create_payload["description"]

