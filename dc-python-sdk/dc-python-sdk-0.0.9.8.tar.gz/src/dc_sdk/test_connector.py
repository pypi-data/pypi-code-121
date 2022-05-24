from . import errors
import pytest


class TestGeneral:
    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.general
    def test_stores_credentials(self, connector, good_credentials):
        assert connector.credentials == good_credentials

    def test_env_has_object_id(self, good_credentials):
        assert "object_id" in good_credentials


class TestAuth:
    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.authenticate
    def test_pass_returns_bool(self, good_authentication):
        results = good_authentication
        assert type(results) is bool

    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.authenticate
    def test_pass_returns_true(self, good_authentication):
        results = good_authentication
        assert results

    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.authenticate
    def test_no_credentials_raises_authentication_error(self, connector_class):
        _connector = connector_class.Connector(None)
        with pytest.raises(errors.AuthenticationError):
            _connector.authenticate()


class TestGetObjects:
    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.get_objects
    def test_pass_returns(self, get_good_objects):
        # Since we are using a test account, we should have made some objects when we made the account
        assert get_good_objects

    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.get_objects
    def test_pass_returns_list(self, get_good_objects):
        assert type(get_good_objects) is list

    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.get_objects
    def test_pass_returns_nonempty_list(self, get_good_objects):
        assert len(get_good_objects) > 0

    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.get_objects
    def test_pass_returns_dicts_in_list(self, get_good_objects):
        objects = get_good_objects
        for obj in objects:
            assert type(obj) is dict

    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.get_objects
    def test_pass_returns_nonempty_dicts_in_list(self, get_good_objects):
        objects = get_good_objects
        for obj in objects:
            assert len(obj) > 0

    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.get_objects
    def test_pass_returns_object_id_in_dict(self, get_good_objects):
        objects = get_good_objects
        for obj in objects:
            assert "object_id" in obj

    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.get_objects
    def test_pass_returns_object_name_in_dict(self, get_good_objects):
        objects = get_good_objects
        for obj in objects:
            assert "object_name" in obj

    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.get_objects
    def test_pass_returns_object_label_in_dict(self, get_good_objects):
        objects = get_good_objects
        for obj in objects:
            assert "object_label" in obj

    @pytest.mark.source
    @pytest.mark.destination
    @pytest.mark.get_objects
    def test_pass_returns_object_group_in_dict(self, get_good_objects):
        objects = get_good_objects
        for obj in objects:
            assert "object_group" in obj

    # # FIXME: make this test an empty account
    # def test_fail_empty_account(self, get_good_objects):
    #     with not pytest.raises(errors.NoObjectsFoundError):
    #         objects = get_good_objects
    #         pass


class TestGetFields:

    @pytest.mark.source
    @pytest.mark.get_fields
    def test_pass_returns_list(self, get_good_fields):
        results = get_good_fields
        assert type(results) is list

    @pytest.mark.source
    @pytest.mark.get_fields
    def test_pass_returns_nonempty_list(self, get_good_fields):
        results = get_good_fields
        assert len(results) > 0

    @pytest.mark.source
    @pytest.mark.get_fields
    def test_pass_returns_dicts_in_list(self, get_good_fields):
        fields = get_good_fields
        for field in fields:
            assert type(field) is dict

    @pytest.mark.source
    @pytest.mark.get_fields
    def test_pass_returns_nonempty_dicts_in_list(self, get_good_fields):
        fields = get_good_fields
        for field in fields:
            assert len(field) > 0

    @pytest.mark.source
    @pytest.mark.get_fields
    def test_pass_returns_field_id_in_dict(self, get_good_fields):
        fields = get_good_fields
        for field in fields:
            assert "field_id" in field

    @pytest.mark.source
    @pytest.mark.get_fields
    def test_pass_returns_field_name_in_dict(self, get_good_fields):
        fields = get_good_fields
        for field in fields:
            assert "field_name" in field

    @pytest.mark.source
    @pytest.mark.get_fields
    def test_pass_returns_field_label_in_dict(self, get_good_fields):
        fields = get_good_fields
        for field in fields:
            assert "field_label" in field

    @pytest.mark.source
    @pytest.mark.get_fields
    def test_pass_returns_data_type_in_dict(self, get_good_fields):
        fields = get_good_fields
        for field in fields:
            assert "data_type" in field

    @pytest.mark.source
    @pytest.mark.get_fields
    def test_pass_returns_size_in_dict(self, get_good_fields):
        fields = get_good_fields
        for field in fields:
            assert "size" in field

    @pytest.mark.source
    @pytest.mark.get_fields
    def test_fail_bad_object_id_throws_error(self, bad_object_id, connector):
        with pytest.raises(errors.BadObjectIDError):
            connector.authenticate()
            connector.get_fields(bad_object_id)


class TestGetData:
    @pytest.mark.source
    @pytest.mark.get_data
    def test_pass_returns(self, get_good_data_small):
        # Since we are using a test account, we should have made some data for the selected object_id
        data = get_good_data_small
        assert data

    @pytest.mark.source
    @pytest.mark.get_data
    def test_pass_returns_dict(self, get_good_data_small):
        data = get_good_data_small
        assert type(data) is dict

    @pytest.mark.source
    @pytest.mark.get_data
    def test_pass_returns_data_in_dict(self, get_good_data_small):
        data = get_good_data_small
        assert "data" in data

    @pytest.mark.source
    @pytest.mark.get_data
    def test_pass_returns_data_as_list(self, get_good_data_small):
        data = get_good_data_small
        assert type(data["data"]) is list

    @pytest.mark.source
    @pytest.mark.get_data
    def test_pass_returns_nonempty_list(self, get_good_data_small):
        data = get_good_data_small
        assert len(data["data"]) > 0

    @pytest.mark.source
    @pytest.mark.get_data
    def test_pass_returns_dicts_in_list(self, get_good_data_small):
        data = get_good_data_small
        for obj in data["data"]:
            assert type(obj) is dict

    @pytest.mark.source
    @pytest.mark.get_data
    def test_pass_filters_by_field_id(self, good_object_id, get_three_good_field_ids, connector):
        connector.authenticate()
        data = connector.get_data(good_object_id, get_three_good_field_ids)
        assert len(data["data"][0].keys()) == len(get_three_good_field_ids)

    @pytest.mark.source
    @pytest.mark.get_data
    def test_fail_bad_field_id_throws_error(self, good_object_id, bad_field_ids, connector):
        with pytest.raises(errors.BadFieldIDError):
            connector.authenticate()
            connector.get_data(good_object_id, bad_field_ids)

    # @pytest.mark.get_fields
    # def test_fail_filter_data_type_throws_error(self, good_object_id, get_all_good_field_ids, connector):
    #     with pytest.raises(errors.FilterDataTypeError):
    #         connector.authenticate()
    #         connector.get_data(good_object_id, get_all_good_field_ids,)

    @pytest.mark.source
    @pytest.mark.get_data
    def test_pass_returns_nonempty_dicts_in_list(self, get_good_data_small):
        data = get_good_data_small
        for obj in data["data"]:
            assert len(obj) > 0

    @pytest.mark.source
    @pytest.mark.get_data
    def test_pass_returns_next_page_flag(self, get_good_data_small):
        data = get_good_data_small
        assert "next_page" in data


class TestGetMetaData:
    @pytest.mark.destination
    @pytest.mark.get_meta_data
    def test_pass_returns_column_type_flg(self, get_good_meta_data):
        data = get_good_meta_data
        assert "column_type_flg" in data

    @pytest.mark.destination
    @pytest.mark.get_meta_data
    def test_pass_returns_size_flg(self, get_good_meta_data):
        data = get_good_meta_data
        assert "size_flg" in data

    @pytest.mark.destination
    @pytest.mark.get_meta_data
    def test_pass_returns_new_object_regex(self, get_good_meta_data):
        data = get_good_meta_data
        assert "new_object_regex" in data

    @pytest.mark.destination
    @pytest.mark.get_meta_data
    def test_pass_returns_size_regex(self, get_good_meta_data):
        data = get_good_meta_data
        assert "size_regex" in data

    @pytest.mark.destination
    @pytest.mark.get_meta_data
    def test_pass_returns_data_types(self, get_good_meta_data):
        data = get_good_meta_data
        assert "data_types" in data

