from moto import mock_s3
from tempfile import NamedTemporaryFile


@mock_s3
def test_bucket_put(bucket):
    bucket.create()

    file_text = "test"
    response = bucket.put("text.txt", file_text)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


@mock_s3
def test_bucket_get(bucket):
    bucket.create()

    file_text = "test"
    response = bucket.put("text.txt", file_text)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    data, metadata = bucket.get("text.txt")
    assert data == "test"


@mock_s3
def test_bucket_delete(bucket):
    bucket.create()

    file_text = "test"
    response = bucket.put("text.txt", file_text)
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    response = bucket.delete("text.txt")
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 204


@mock_s3
def test_bucket_upload(bucket):
    bucket.create()

    file_text = "test"
    with NamedTemporaryFile(delete=True, suffix=".txt") as upload:
        with open(upload.name, "w", encoding="UTF-8") as f:
            f.write(file_text)

        success = bucket.upload_file(upload.name, upload.name)

    assert success is True


@mock_s3
def test_bucket_download(bucket):
    bucket.create()

    file_text = "test"
    with NamedTemporaryFile(delete=True, suffix=".txt") as upload:
        with open(upload.name, "w", encoding="UTF-8") as f:
            f.write(file_text)

        success = bucket.upload_file(upload.name, upload.name)

    assert success is True

    with NamedTemporaryFile(delete=True, suffix=".txt") as download:
        success = bucket.download_file(upload.name, download.name)
        assert success is True

        with open(download.name, encoding="UTF-8") as f:
            assert f.read() == "test"


@mock_s3
def test_list_all(bucket):
    bucket.create()

    file_names = ["test.txt", "dir1/test.txt", "dir1/dir2/test.txt"]
    for file_name in file_names:
        response = bucket.put(file_name, "test")
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    file_list = bucket.list_all()
    assert len(file_list) == 3


@mock_s3
def test_list_dir_root(bucket):
    bucket.create()

    file_names = ["test.txt", "dir1/test.txt", "dir1/dir2/test.csv"]
    for file_name in file_names:
        response = bucket.put(file_name, "test")
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    file_list = bucket.list_dir()
    assert len(file_list) == 1


@mock_s3
def test_list_dir_recursive(bucket):
    bucket.create()

    file_names = ["test.txt", "dir1/test.txt", "dir1/dir2/test.csv"]
    for file_name in file_names:
        response = bucket.put(file_name, "test")
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    file_list = bucket.list_dir(recursive=True)
    assert len(file_list) == 3


@mock_s3
def test_list_dir_ext_no_recursive(bucket):
    bucket.create()

    file_names = ["test.txt", "dir1/test.txt", "dir1/dir2/test.csv"]
    for file_name in file_names:
        response = bucket.put(file_name, "test")
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    file_list = bucket.list_dir(filter_ext="csv")

    assert file_list == []


@mock_s3
def test_list_dir_ext_recursive(bucket):
    bucket.create()

    file_names = ["test.txt", "dir1/test.txt", "dir1/dir2/test.csv"]
    for file_name in file_names:
        response = bucket.put(file_name, "test")
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    file_list = bucket.list_dir(recursive=True, filter_ext="csv")

    assert len(file_list) == 1
    assert file_list[0] == "dir1/dir2/test.csv"


@mock_s3
def test_list_dir_ext_recursive_names_only(bucket):
    bucket.create()

    file_names = ["test.txt", "dir1/test.txt", "dir1/dir2/test2.csv"]
    for file_name in file_names:
        response = bucket.put(file_name, "test")
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    file_list = bucket.list_dir(recursive=True, filter_ext="csv", names_only=True)

    assert len(file_list) == 1
    assert file_list[0] == "test2"


@mock_s3
def test_list_dir_ext_path(bucket):
    bucket.create()

    file_names = ["test.txt", "dir1/test.txt", "dir1/test.csv", "dir1/dir2/test.csv"]
    for file_name in file_names:
        response = bucket.put(file_name, "test")
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    file_list = bucket.list_dir(path="dir1", filter_ext="csv")

    assert len(file_list) == 1
    assert file_list[0] == "dir1/test.csv"
