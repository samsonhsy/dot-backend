# tests/helpers/utils.py
import json
import io
import zipfile

USERS_PREFIX = "/users"
AUTH_PREFIX = "/auth"
ADMIN_PREFIX = "/admin"
COLLECTIONS_PREFIX = "/collections"

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

def promote_user(mock_client, user_id, to_tier):
    user_promote_request = {
        "user_id": user_id,
        "to_tier": to_tier
    }

    user_promote_response = mock_client.post(ADMIN_PREFIX + "/promote-user", json=user_promote_request)
    
    user_promote_status_code = user_promote_response.status_code
    assert user_promote_status_code == 200

def generate_license_keys(mock_client, quantity):
    generate_license_response = mock_client.post(ADMIN_PREFIX + "/license", json={"quantity" : quantity})
    
    generate_license_status_code = generate_license_response.status_code
    assert generate_license_status_code == 201

    generate_license_json = generate_license_response.json()

    return generate_license_json

def list_license_keys(mock_client):
    list_license_keys_response = mock_client.get(ADMIN_PREFIX + "/license")

    list_license_keys_status_code = list_license_keys_response.status_code
    assert list_license_keys_status_code == 200

    list_license_keys_json = list_license_keys_response.json()

    return list_license_keys_json

def get_license_key_payload(license_key):
    return {
        "key_string" : license_key
    }

def create_new_collection(mock_client, collection_create_payload, authorization_headers):
    collection_create_response = mock_client.post(COLLECTIONS_PREFIX + "/", json=collection_create_payload, headers=authorization_headers)

    collection_create_status_code = collection_create_response.status_code
    assert collection_create_status_code == 201

    collection_create_json = collection_create_response.json()

    return collection_create_json

def add_to_collection(mock_client, collection_id, collection_add_payload, mock_files, authorization_headers):
    collection_add_payload["collection_id"] = collection_id
    collection_add_data = {"collection_add_payload": json.dumps(collection_add_payload)}

    collection_add_response = mock_client.post(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", data=collection_add_data, files=mock_files, headers=authorization_headers)

    collection_add_status_code = collection_add_response.status_code
    assert collection_add_status_code == 201

    collection_add_json = collection_add_response.json()

    return collection_add_json

def get_collection_list_of_user(mock_client, authorization_headers):
    get_collection_list_response = mock_client.get(COLLECTIONS_PREFIX + "/owned", headers=authorization_headers)

    get_collection_list_status_code = get_collection_list_response.status_code
    assert get_collection_list_status_code == 200

    get_collection_list_json = get_collection_list_response.json()
    
    return get_collection_list_json

def get_collection_content(mock_client, collection_id, authorization_headers):
    files_content = []

    get_collection_content_response = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/archive", headers=authorization_headers)
    
    get_collection_content_status_code = get_collection_content_response.status_code
    assert get_collection_content_status_code == 200

    byte_data = io.BytesIO(get_collection_content_response.content)

    with zipfile.ZipFile(byte_data, "r") as archive:
        archive_filenames = archive.namelist()

        for index, archive_filename in enumerate(archive_filenames):
            archive_file_content = archive.open(archive_filename).read().decode()

            files_content.append({
                "filename": archive_filename,
                "content": archive_file_content
                })

    return files_content

def get_collection_file_paths(mock_client, collection_id, authorization_headers):
    get_collection_file_paths_response = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", headers=authorization_headers)

    get_collection_file_paths_status_code = get_collection_file_paths_response.status_code
    assert get_collection_file_paths_status_code == 200

    get_collection_file_paths_json = get_collection_file_paths_response.json()

    return get_collection_file_paths_json

def seperate_mock_files(mock_files):
    mock_filenames = [mock_files[n][1][0] for n in range(len(mock_files))]    
    mock_file_contents = [mock_files[n][1][1].getvalue().decode("utf-8") for n in range(len(mock_files))]

    return mock_filenames, mock_file_contents

def seperate_collection_content(collection_content):
    collection_content_filenames = [file["filename"] for file in collection_content]
    collection_content_file_contents = [file["content"] for file in collection_content]

    return collection_content_filenames, collection_content_file_contents