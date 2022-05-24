import datetime


def test_api_heartbeat_invoke(runner, mocker_patch_provider):
    data = {"status": 200, "actions": []}
    mocker_patch_provider.save_camera_heartbeat.side_effect = lambda *args: data
    from rebotics_sdk.cli.hawkeye import api
    result = runner.invoke(api, ['heartbeat', '-c',
                                 'test_camera',
                                 '-b', '0.55',
                                 '-f', '0.76',
                                 '-u', '0.25'])
    mocker_patch_provider.save_camera_heartbeat.assert_called_once_with('test_camera', 0.55, 0.76, 0.25)
    assert result.exit_code == 0
    assert not result.exception
    assert str(data) in result.output.strip()


def test_api_heartbeat_invoke_without_camera(runner, mocker_patch_provider):
    from rebotics_sdk.cli.hawkeye import api
    result = runner.invoke(api, ['heartbeat',
                                 '-b', '0.55',
                                 '-f', '0.76',
                                 '-u', '0.25'])
    assert result.exit_code == 2
    assert result.exception
    assert "Missing option '-c' / '--camera'" in result.output.strip()


def test_api_fixture_invoke(runner, mocker_patch_provider):
    data = {
        "id": 1,
        "created": datetime.datetime(2021, 9, 16, 10, 33, 45, 582912),
        "modified": datetime.datetime(2021, 9, 16, 10, 33, 45, 582912),
        "store_id": "storetest",
        "aisle": "aisletest",
        "section": "sectiontest",
        "retailer": "testretailer"
    }
    mocker_patch_provider.save_fixture.side_effect = lambda *args: data
    from rebotics_sdk.cli.hawkeye import api
    result = runner.invoke(
        api,
        [
            'fixture',
            '-i', 'storetest',
            '-r', 'testretailer',
            '-a', 'aisletest',
            '-s', 'sectiontest'
        ]
    )
    mocker_patch_provider.save_fixture.assert_called_once_with(
        'storetest',
        'aisletest',
        'sectiontest',
        'testretailer'
    )
    assert result.exit_code == 0
    assert not result.exception
    assert str(data) in result.output


def test_api_fixture_invoke_without_option(runner, mocker_patch_provider):
    from rebotics_sdk.cli.hawkeye import api
    result = runner.invoke(
        api,
        [
            'fixture',
            '-i', 'storetest'
        ]
    )
    assert result.exit_code == 2
    assert result.exception
    assert "Missing option" in result.output


def test_get_fixtures_invoke(runner, mocker_patch_provider):
    data = []
    mocker_patch_provider.get_fixtures.side_effect = lambda *args: data
    from rebotics_sdk.cli.hawkeye import api
    result = runner.invoke(
        api,
        ['fixtures']
    )
    mocker_patch_provider.get_fixtures.assert_called()
    assert result.exit_code == 0
    assert not result.exception
    assert str(data) in result.output.strip()


def test_api_camera_invoke(runner, mocker_patch_provider):
    data = {
        "id": 1,
        "created": datetime.datetime(2021, 9, 16, 10, 33, 45, 582912),
        "modified": datetime.datetime(2021, 9, 16, 10, 33, 45, 582912),
        "camera_id": "testcameraid",
        "added_by": 1,
        "aisle": 1,
        "section": 1
    }
    mocker_patch_provider.create_shelf_camera.side_effect = lambda *args: data
    from rebotics_sdk.cli.hawkeye import api
    result = runner.invoke(
        api,
        [
            'camera',
            '-c', 'testcameraid',
            '-a', '1',
            '-f', '1'
        ]
    )
    mocker_patch_provider.create_shelf_camera.assert_called_once_with(
        'testcameraid',
        1,
        1
    )
    assert result.exit_code == 0
    assert not result.exception
    assert str(data) in result.output.strip()


def test_api_camera_invoke_without_option(runner, mocker_patch_provider):
    from rebotics_sdk.cli.hawkeye import api
    result = runner.invoke(
        api,
        [
            'camera',
            '-c', 'testcameraid'
        ]
    )
    assert result.exit_code == 2
    assert result.exception
    assert "Missing option" in result.output.strip()


def test_get_list_shelf_cameras(runner, mocker_patch_provider):
    mocker_patch_provider.get_shelf_cameras.side_effect = lambda *args: []
    from rebotics_sdk.cli.hawkeye import api
    result = runner.invoke(
        api,
        ['cameras']
    )
    mocker_patch_provider.get_shelf_cameras.assert_called()
    assert result.exit_code == 0
    assert not result.exception
    assert str([]) in result.output.strip()


def test_api_capture_invoke(runner, mocker_patch_provider):
    data = {"Message": "Capture created"}
    mocker_patch_provider.save_capture.side_effect = lambda *args: data
    from rebotics_sdk.cli.hawkeye import api
    result = runner.invoke(
        api,
        [
            'capture',
            '-c', 'test_camera_id',
            '-f', '/shelf_camera/testcameraid/2020/02/01/filename_11:01.jpeg',
            '-b', 'sftp-bucket'
        ]
    )
    mocker_patch_provider.save_capture.assert_called_once_with(
        'test_camera_id',
        '/shelf_camera/testcameraid/2020/02/01/filename_11:01.jpeg',
        'sftp-bucket'
    )
    assert result.exit_code == 0
    assert not result.exception
    assert str(data) in result.output.strip()

