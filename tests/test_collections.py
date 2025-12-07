# tests/test_collections.py
import pytest
import utils
import json

import io
import zipfile

from app.services.dotfile_service import generate_dotfile_name_in_collection 
from app.core.settings import settings

COLLECTIONS_PREFIX = "/collections"

FILE_INDICES_PARAMETERS = [0, 1]
USER_TIER_PARAMETERS = ["pro", "admin"]

FREE_TIER_RETRIEVAL_LIMIT = settings.FREE_TIER_RETRIEVAL_LIMIT

# collection creation tests
def test_create_collection(mock_client, user_create_payload, collection_create_payload):
    """
    Verifies that the api can properly create a collection
    """
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




# collection listing tests
def test_get_my_collections(mock_client, user_create_payload, collection_create_payload):
    """
    Verifies that the api returns a list of collections owned by a user
    """
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

def test_get_public_collections(mock_client, user_create_payload, collection_create_payload):
    """
    Verifies that the api returns a list of public collections
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a private collection
    private_collection_create_payload = collection_create_payload.copy()
    private_collection_name = "private_mock_collection"

    private_collection_create_payload["name"] = private_collection_name
    private_collection_create_payload["is_private"] = True
 
    utils.create_new_collection(mock_client, private_collection_create_payload, authorization_headers)

    # create a public collection
    public_collection_create_payload = collection_create_payload.copy()
    public_collection_name = "public_mock_collection"

    public_collection_create_payload["name"] = public_collection_name
    public_collection_create_payload["is_private"] = False

    utils.create_new_collection(mock_client, public_collection_create_payload, authorization_headers)

    # get a list of only public collections
    public_collections_response = mock_client.get(COLLECTIONS_PREFIX + "/public")

    public_collections_status_code = public_collections_response.status_code
    assert public_collections_status_code == 200

    public_collections_json = public_collections_response.json()

    assert len(public_collections_json) == 1
    assert public_collections_json[0]["name"] == public_collection_name
    



# collection content addition tests
def test_valid_add_to_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files):
    """
    Verifies that the api can properly add files to a collection
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # add mock files to collection
    collection_add_payload["collection_id"] = collection_id
    collection_add_data = {"collection_add_payload": json.dumps(collection_add_payload)}

    collection_add_response = mock_client.post(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", data=collection_add_data, files=mock_files, headers=authorization_headers)

    collection_add_status_code = collection_add_response.status_code
    assert collection_add_status_code == 201

    # check if file data in database is correct
    collection_add_json = collection_add_response.json()

    assert collection_add_json[0]["path"] == collection_add_payload["content"][0]["path"]  
    assert collection_add_json[0]["filename"] == collection_add_payload["content"][0]["filename"]  
    
    assert collection_add_json[1]["path"] == collection_add_payload["content"][1]["path"]  
    assert collection_add_json[1]["filename"] == collection_add_payload["content"][1]["filename"]  

def test_add_to_collection_with_mismatch_collection_id(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files):
    """
    Verifies that the api rejects attempts to add files to a collection by providing different collection ids in the api endpoint and request data
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # attempt to add mock files to collection
    invalid_collection_id = collection_id + 1

    collection_add_payload["collection_id"] = invalid_collection_id
    collection_add_data = {"collection_add_payload": json.dumps(collection_add_payload)}

    collection_add_response = mock_client.post(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", data=collection_add_data, files=mock_files, headers=authorization_headers)

    collection_add_status_code = collection_add_response.status_code
    assert collection_add_status_code == 400

    collection_add_json = collection_add_response.json()
    assert collection_add_json["detail"] == f"Body collection_id ({collection_add_payload["collection_id"]}) must match URL collection_id ({collection_id})"

def test_add_to_collection_with_excess_file_count(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files):
    """
    Verifies that the api rejects attempts to add files to a collection by providing more files than those specified in the request data 
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # attempt to add mock files to collection
    collection_add_payload["collection_id"] = collection_id

    # only include the first file path and filename in collection_add_payload
    collection_add_payload["content"] = collection_add_payload["content"][:1]
    collection_add_data = {"collection_add_payload": json.dumps(collection_add_payload)}

    collection_add_response = mock_client.post(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", data=collection_add_data, files=mock_files, headers=authorization_headers)

    collection_add_status_code = collection_add_response.status_code
    assert collection_add_status_code == 400

    collection_add_json = collection_add_response.json()
    assert collection_add_json["detail"] == f"Number of files ({len(mock_files)}) must match number of content entries ({len(collection_add_payload["content"])})"

def test_add_to_collection_with_insufficient_file_count(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files):
    """
    Verifies that the api rejects the attempt to add files to a collection by providing less files than those specified in the request data
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # only include first mock file
    mock_files = mock_files[:1]

    # attempt to add mock files to collection
    collection_add_payload["collection_id"] = collection_id
    collection_add_data = {"collection_add_payload": json.dumps(collection_add_payload)}


    collection_add_response = mock_client.post(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", data=collection_add_data, files=mock_files, headers=authorization_headers)

    collection_add_status_code = collection_add_response.status_code
    
    assert collection_add_status_code == 400

    # check if file data in database is correct
    collection_add_json = collection_add_response.json()

    assert collection_add_json["detail"] == f"Number of files ({len(mock_files)}) must match number of content entries ({len(collection_add_payload["content"])})"

@pytest.mark.parametrize("mismatch_index", FILE_INDICES_PARAMETERS)
def test_add_to_collection_with_mismatch_filenames(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files, mismatch_index):
    """
    Verifies that the api rejects attempts to add files to a collection by providing files with different filenames than those specified in the request data
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # attempt to add mock files to collection
    collection_add_payload["collection_id"] = collection_id
    
    # change filename of collection_add_payload at {mismatch_index}
    collection_add_payload["content"][mismatch_index]["filename"] = "invalid_mock_filename"

    collection_add_data = {"collection_add_payload": json.dumps(collection_add_payload)}

    collection_add_response = mock_client.post(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", data=collection_add_data, files=mock_files, headers=authorization_headers)

    collection_add_status_code = collection_add_response.status_code
    assert collection_add_status_code == 400

    # check if file data in database is correct
    file_filename = mock_files[mismatch_index][1][0]
    content_filename = collection_add_payload["content"][mismatch_index]["filename"]

    collection_add_json = collection_add_response.json()
    assert collection_add_json["detail"] == f"Filename mismatch at index {mismatch_index}: uploaded file is '{file_filename}' but content specifies '{content_filename}'"

def test_add_to_invalid_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files):
    """
    Verifies that the api rejects attempts to add files to a non-existant collection
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create an invalid collection id
    collection_id = 1

    # attempt to add mock files to invalid collection
    collection_add_payload["collection_id"] = collection_id
    collection_add_data = {"collection_add_payload": json.dumps(collection_add_payload)}

    collection_add_response = mock_client.post(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", data=collection_add_data, files=mock_files, headers=authorization_headers)

    collection_add_status_code = collection_add_response.status_code
    assert collection_add_status_code == 404
    
    collection_add_json = collection_add_response.json()
    assert collection_add_json["detail"] == f"Collection {collection_id} not found"

def test_add_to_unowned_private_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files):
    """
    Verifies that the api rejects attempts to add files to a private collection that the user does not own 
    """
    # create the first user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication for the first user
    user_login_payload_0 = utils.get_user_login_payload(user_create_payload)
    access_token_0 = utils.get_user_access_token(mock_client, user_login_payload_0)
    
    authorization_headers_0 = utils.get_authorization_headers(access_token_0)

    # create a private collection for first user
    collection_create_payload["is_private"] = True

    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers_0)
    collection_id = collection_create_json["id"]

    # create the second user
    user_create_payload["username"] = "new_mock_user"
    user_create_payload["email"] = "new_mock_email@email.com"

    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for the second user
    user_login_payload_1 = utils.get_user_login_payload(user_create_payload)
    access_token_1 = utils.get_user_access_token(mock_client, user_login_payload_1)
    
    authorization_headers_1 = utils.get_authorization_headers(access_token_1)

    # attempt to add mock files to collection without access permission
    collection_add_payload["collection_id"] = collection_id
    collection_add_data = {"collection_add_payload": json.dumps(collection_add_payload)}

    collection_add_response = mock_client.post(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", data=collection_add_data, files=mock_files, headers=authorization_headers_1)

    collection_add_status_code = collection_add_response.status_code
    assert collection_add_status_code == 403
    
    collection_add_json = collection_add_response.json()
    assert collection_add_json["detail"] == "You do not have permission to access this collection"




# collection content retrieval tests
def test_valid_get_collection_content(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files):
    """
    Verifies that the api returns files from a collection
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # add mock files to collection
    utils.add_to_collection(mock_client, collection_id, collection_add_payload, mock_files, authorization_headers)

    # check files in collection
    get_collection_content_response = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/archive", headers=authorization_headers)

    get_collection_content_status_code = get_collection_content_response.status_code
    assert get_collection_content_status_code == 200

    # convert the bytes response content to a zip file
    byte_data = io.BytesIO(get_collection_content_response.content)

    with zipfile.ZipFile(byte_data, "r") as archive:
        archive_filenames = archive.namelist()
        mock_filenames = [mock_files[n][1][0] for n in range(len(mock_files))]
        mock_file_contents = [mock_files[n][1][1].getvalue().decode("utf-8") for n in range(len(mock_files))]

        # check if number of file retrieved is the same as the number of files uploaded
        assert len(archive_filenames) == len(mock_filenames)
        
        # check that each file is retrieved is correct
        for index, archive_filename in enumerate(archive_filenames):
            mock_filename_in_collection = generate_dotfile_name_in_collection(collection_id, mock_filenames[index])
            mock_file_content = mock_file_contents[index]
            archive_file_content = archive.open(archive_filename).read().decode()

            assert archive_filename == mock_filename_in_collection
            assert archive_file_content == mock_file_content

def test_get_collection_content_retrieval_limit_for_free_user(mock_client, user_create_payload, collection_create_payload):
    """
    Verifies that the api limits the number of file retrievals from a collection for free users
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # check files in collection until the retrieval limit is just reached
    for _ in range(FREE_TIER_RETRIEVAL_LIMIT):
        get_collection_content_response_0 = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/archive", headers=authorization_headers)

        get_collection_content_status_code_0 = get_collection_content_response_0.status_code
        assert get_collection_content_status_code_0 == 200

    # attempt to check files in collection after retrieval limit is reached
    get_collection_content_response_1 = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/archive", headers=authorization_headers)

    get_collection_content_status_code_1 = get_collection_content_response_1.status_code
    assert get_collection_content_status_code_1 == 429

    get_collection_content_json_1 = get_collection_content_response_1.json()
    assert get_collection_content_json_1["detail"] == f"You have exceeded your monthly limit of {FREE_TIER_RETRIEVAL_LIMIT} retrievals. Please upgrade to a Pro account for unlimited access."

@pytest.mark.parametrize("user_tier", USER_TIER_PARAMETERS)
def test_get_collection_content_retrieval_limit_for_nonfree_user(mock_client_with_admin_tier, user_create_payload, collection_create_payload, user_tier):
    """
    Verifies that the api allows for unlimited file retrievals from a collection for non-free users
    """
    # rename for convenience
    mock_client = mock_client_with_admin_tier
    
    # create a user
    user_create_json = utils.create_new_user(mock_client, user_create_payload)
    user_id = user_create_json["id"]

    # promote user
    utils.promote_user(mock_client, user_id, user_tier)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # check files in collection until the retrieval limit is just reached
    for _ in range(FREE_TIER_RETRIEVAL_LIMIT):
        get_collection_content_response_0 = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/archive", headers=authorization_headers)

        get_collection_content_status_code_0 = get_collection_content_response_0.status_code
        assert get_collection_content_status_code_0 == 200

    # attempt to check files in collection after retrieval limit is reached
    get_collection_content_response_1 = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/archive", headers=authorization_headers)

    get_collection_content_status_code_1 = get_collection_content_response_1.status_code
    assert get_collection_content_status_code_1 == 200

def test_get_collection_content_from_invalid_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload):
    """
    Verifies that the api rejects attempts to retrieve files from a non-existant collection
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create an invalid collection id
    collection_id = 1

    # attempt to get file content of invalid collection
    get_collection_content_response = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/archive", headers=authorization_headers)

    get_collection_content_status_code = get_collection_content_response.status_code
    assert get_collection_content_status_code == 404

    get_collection_content_json = get_collection_content_response.json()
    assert get_collection_content_json["detail"] == f"Collection {collection_id} not found"

def test_get_collection_content_of_unowned_private_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload):
    """
    Verifies that the api rejects attempts to retrieve files from a private collection that the user does not own
    """
    # create the first user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication for the first user
    user_login_payload_0 = utils.get_user_login_payload(user_create_payload)
    access_token_0 = utils.get_user_access_token(mock_client, user_login_payload_0)
    
    authorization_headers_0 = utils.get_authorization_headers(access_token_0)

    # create a private collection for first user
    collection_create_payload["is_private"] = True

    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers_0)
    collection_id = collection_create_json["id"]

    # create the second user
    user_create_payload["username"] = "new_mock_user"
    user_create_payload["email"] = "new_mock_email@email.com"

    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for the second user
    user_login_payload_1 = utils.get_user_login_payload(user_create_payload)
    access_token_1 = utils.get_user_access_token(mock_client, user_login_payload_1)
    
    authorization_headers_1 = utils.get_authorization_headers(access_token_1)

    # attempt to get file content of collection without access permission
    get_collection_content_response = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/archive", headers=authorization_headers_1)

    get_collection_content_status_code = get_collection_content_response.status_code
    assert get_collection_content_status_code == 403

    get_collection_content_json = get_collection_content_response.json()
    assert get_collection_content_json["detail"] == "You do not have permission to access this collection"




# collection file paths retrieval tests
def test_valid_get_collection_file_paths(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files):
    """
    Verifies that the api returns a list of file path information of files from a collection
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # add mock files to collection
    utils.add_to_collection(mock_client, collection_id, collection_add_payload, mock_files, authorization_headers)

    # check file paths in collection
    get_collection_file_paths_response = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", headers=authorization_headers)

    get_collection_file_paths_status_code = get_collection_file_paths_response.status_code
    assert get_collection_file_paths_status_code == 200

    get_collection_file_paths_json = get_collection_file_paths_response.json()

    assert get_collection_file_paths_json[0]["path"] == collection_add_payload["content"][0]["path"]
    assert get_collection_file_paths_json[0]["filename"] == collection_add_payload["content"][0]["filename"]

    assert get_collection_file_paths_json[1]["path"] == collection_add_payload["content"][1]["path"]
    assert get_collection_file_paths_json[1]["filename"] == collection_add_payload["content"][1]["filename"]

def test_get_collection_file_paths_from_invalid_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload):
    """
    Verifies that the api rejects attempts to retrieve file path information of files from a non-existant collection
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create an invalid collection id
    collection_id = 1

    # attempt to get file paths of invalid collection
    get_collection_file_paths_response = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", headers=authorization_headers)

    get_collection_file_paths_status_code = get_collection_file_paths_response.status_code
    assert get_collection_file_paths_status_code == 404

    get_collection_file_paths_json = get_collection_file_paths_response.json()
    assert get_collection_file_paths_json["detail"] == f"Collection {collection_id} not found"

def test_get_collection_file_paths_of_unowned_private_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload):
    """
    Verifies that the api rejects attempts to retrieve file path information from a private collection that the user does not own
    """
    # create the first user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication for the first user
    user_login_payload_0 = utils.get_user_login_payload(user_create_payload)
    access_token_0 = utils.get_user_access_token(mock_client, user_login_payload_0)
    
    authorization_headers_0 = utils.get_authorization_headers(access_token_0)

    # create a private collection for first user
    collection_create_payload["is_private"] = True

    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers_0)
    collection_id = collection_create_json["id"]

    # create the second user
    user_create_payload["username"] = "new_mock_user"
    user_create_payload["email"] = "new_mock_email@email.com"

    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for the second user
    user_login_payload_1 = utils.get_user_login_payload(user_create_payload)
    access_token_1 = utils.get_user_access_token(mock_client, user_login_payload_1)
    
    authorization_headers_1 = utils.get_authorization_headers(access_token_1)

    # attempt to get file paths of collection without access permission
    get_collection_file_paths_response = mock_client.get(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles", headers=authorization_headers_1)

    get_collection_file_paths_status_code = get_collection_file_paths_response.status_code
    assert get_collection_file_paths_status_code == 403

    get_collection_file_paths_json = get_collection_file_paths_response.json()
    assert get_collection_file_paths_json["detail"] == "You do not have permission to access this collection"




# collection content deletion tests
@pytest.mark.parametrize("delete_index", FILE_INDICES_PARAMETERS)
def test_valid_delete_file_in_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files, delete_index):
    """
    Verifies that the api can properly delete files in a collection
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # add mock files to collection
    utils.add_to_collection(mock_client, collection_id, collection_add_payload, mock_files, authorization_headers)

    # check files in collection in s3 bucket
    get_collection_content_0 = utils.get_collection_content(mock_client, collection_id, authorization_headers)
    assert len(get_collection_content_0) == len(mock_files)

    mock_filenames_0, mock_file_contents_0 = utils.seperate_mock_files(mock_files)
    modified_mock_filenames_0 = [generate_dotfile_name_in_collection(collection_id, mock_filename) for mock_filename in mock_filenames_0]
    
    collection_content_filenames_0, collection_content_file_contents_0 = utils.seperate_collection_content(get_collection_content_0)

    assert modified_mock_filenames_0 == collection_content_filenames_0
    assert mock_file_contents_0 == collection_content_file_contents_0

    # check file paths in collection in database
    get_collection_file_paths_0 = utils.get_collection_file_paths(mock_client, collection_id, authorization_headers)
    assert get_collection_file_paths_0 == collection_add_payload["content"]

    # delete file in collection
    filename = mock_files[delete_index][1][0]

    del mock_files[delete_index]
    del collection_add_payload["content"][delete_index]

    delete_file_in_collection_response = mock_client.delete(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles/{filename}", headers=authorization_headers)
    
    delete_file_in_collection_status_code = delete_file_in_collection_response.status_code
    assert delete_file_in_collection_status_code == 204

    # check if file in collection is deleted from s3 bucket
    get_collection_content_1 = utils.get_collection_content(mock_client, collection_id, authorization_headers)
    assert len(get_collection_content_1) == len(mock_files)

    mock_filenames_1, mock_file_contents_1 = utils.seperate_mock_files(mock_files)
    modified_mock_filenames_1 = [generate_dotfile_name_in_collection(collection_id, mock_filename) for mock_filename in mock_filenames_1]
    
    collection_content_filenames_1, collection_content_file_contents_1 = utils.seperate_collection_content(get_collection_content_1)

    assert modified_mock_filenames_1 == collection_content_filenames_1
    assert mock_file_contents_1 == collection_content_file_contents_1

    # check if file paths in collection is deleted from database
    get_collection_file_paths_1 = utils.get_collection_file_paths(mock_client, collection_id, authorization_headers)
    assert get_collection_file_paths_1 == collection_add_payload["content"]

def test_delete_invalid_file_in_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files):
    """
    Verifies that the api rejects attempts to delete non-existant files from a collection
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # add mock files to collection
    utils.add_to_collection(mock_client, collection_id, collection_add_payload, mock_files, authorization_headers)

    # attempt to delete invalid file in collection
    filename = "invalid_mock_filename"

    delete_file_in_collection_response = mock_client.delete(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles/{filename}", headers=authorization_headers)
    
    delete_file_in_collection_status_code = delete_file_in_collection_response.status_code
    assert delete_file_in_collection_status_code == 404

    delete_file_collection_json = delete_file_in_collection_response.json()
    assert delete_file_collection_json["detail"] == f"File {filename} not found"

def test_delete_file_in_invalid_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload):
    """
    Verifies that the api rejects attempts to delete files from a non-existant collection
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create an invalid collection id
    collection_id = 1

    # attempt to delete file of invalid collection   
    filename = "mock_filename"
    delete_file_in_collection_response = mock_client.delete(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles/{filename}", headers=authorization_headers)

    delete_file_in_collection_status_code = delete_file_in_collection_response.status_code
    assert delete_file_in_collection_status_code == 404

    delete_file_in_collection_json = delete_file_in_collection_response.json()
    assert delete_file_in_collection_json["detail"] == f"Collection {collection_id} not found"

def test_delete_file_in_unowned_private_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload):
    """
    Verifies that the api rejects attempts to delete files from a private collection that the user does not own
    """
    # create the first user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication for the first user
    user_login_payload_0 = utils.get_user_login_payload(user_create_payload)
    access_token_0 = utils.get_user_access_token(mock_client, user_login_payload_0)
    
    authorization_headers_0 = utils.get_authorization_headers(access_token_0)

    # create a private collection for first user
    collection_create_payload["is_private"] = True

    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers_0)
    collection_id = collection_create_json["id"]

    # create the second user
    user_create_payload["username"] = "new_mock_user"
    user_create_payload["email"] = "new_mock_email@email.com"

    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for the second user
    user_login_payload_1 = utils.get_user_login_payload(user_create_payload)
    access_token_1 = utils.get_user_access_token(mock_client, user_login_payload_1)
    
    authorization_headers_1 = utils.get_authorization_headers(access_token_1)

    # attempt to delete file of collection without access permission   
    filename = "mock_filename"
    delete_file_in_collection_response = mock_client.delete(COLLECTIONS_PREFIX + f"/{collection_id}/dotfiles/{filename}", headers=authorization_headers_1)

    delete_file_in_collection_status_code = delete_file_in_collection_response.status_code
    assert delete_file_in_collection_status_code == 403

    delete_file_in_collection_json = delete_file_in_collection_response.json()
    assert delete_file_in_collection_json["detail"] == "You do not have permission to access this collection"




# collection deletion tests
def test_valid_delete_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload, mock_files):
    """
    Verifies that the api can properly delete collections
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create a collection
    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers)
    collection_id = collection_create_json["id"]

    # check if collection has been added
    get_collection_list_json_0 = utils.get_collection_list_of_user(mock_client, authorization_headers)
    
    assert len(get_collection_list_json_0) == 1

    # add mock files to collection
    collection_add_json = utils.add_to_collection(mock_client, collection_id, collection_add_payload, mock_files, authorization_headers)

    # delete collection
    collection_delete_response = mock_client.delete(COLLECTIONS_PREFIX + f"/{collection_id}", headers=authorization_headers)

    collection_delete_status_code = collection_delete_response.status_code
    assert collection_delete_status_code == 204

    # check if collection has been deleted
    get_collection_list_json_1 = utils.get_collection_list_of_user(mock_client, authorization_headers)
    
    assert len(get_collection_list_json_1) == 0

def test_delete_invalid_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload):
    """
    Verifies that the api rejects attempts to delete non-existant collections
    """
    # create a user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication
    user_login_payload = utils.get_user_login_payload(user_create_payload)
    access_token = utils.get_user_access_token(mock_client, user_login_payload)
    
    authorization_headers = utils.get_authorization_headers(access_token)

    # create an invalid collection id
    collection_id = 1

    # attempt to delete an invalid collection
    delete_collection_response = mock_client.delete(COLLECTIONS_PREFIX + f"/{collection_id}", headers=authorization_headers)
    
    delete_collection_status_code = delete_collection_response.status_code
    assert delete_collection_status_code == 404

    delete_collection_json = delete_collection_response.json()
    assert delete_collection_json["detail"] == f"Collection {collection_id} not found"

def test_delete_unowned_private_collection(mock_client, user_create_payload, collection_create_payload, collection_add_payload):
    """
    Verifies that the api rejects attempts to delete a private collection that the user does not own
    """
    # create the first user
    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for authentication for the first user
    user_login_payload_0 = utils.get_user_login_payload(user_create_payload)
    access_token_0 = utils.get_user_access_token(mock_client, user_login_payload_0)
    
    authorization_headers_0 = utils.get_authorization_headers(access_token_0)

    # create a private collection for first user
    collection_create_payload["is_private"] = True

    collection_create_json = utils.create_new_collection(mock_client, collection_create_payload, authorization_headers_0)
    collection_id = collection_create_json["id"]

    # create the second user
    user_create_payload["username"] = "new_mock_user"
    user_create_payload["email"] = "new_mock_email@email.com"

    utils.create_new_user(mock_client, user_create_payload)

    # get a jwt token for the second user
    user_login_payload_1 = utils.get_user_login_payload(user_create_payload)
    access_token_1 = utils.get_user_access_token(mock_client, user_login_payload_1)
    
    authorization_headers_1 = utils.get_authorization_headers(access_token_1)

    # attempt to delete a collection without access permission
    delete_collection_response = mock_client.delete(COLLECTIONS_PREFIX + f"/{collection_id}", headers=authorization_headers_1)
    
    delete_collection_status_code = delete_collection_response.status_code
    assert delete_collection_status_code == 403

    delete_collection_json = delete_collection_response.json()
    assert delete_collection_json["detail"] == "You do not have permission to access this collection"
