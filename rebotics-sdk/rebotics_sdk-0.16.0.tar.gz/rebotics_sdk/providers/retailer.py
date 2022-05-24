import json

import six

from rebotics_sdk.providers.utils import hash_file, accept_file
from .base import ReboticsBaseProvider, remote_service, PageResult, UniqueRequestProxy
from ..advanced.flows import FeatureVectorFlow


class RetailerProvider(ReboticsBaseProvider):
    proxy_class = UniqueRequestProxy
    proxy_config = {
        'request_uid_header_name': 'REB-CLIENT-REQUEST-UID'
    }

    @remote_service('/api/v4/')
    def api_v4_root(self, **kwargs):
        return self.session.get()

    @remote_service('/api/v4/version/')
    def version(self, *kwargs):
        return self.session.get()

    @remote_service('/api/v4/token-auth/', raw=True)
    def token_auth(self, username, password, **kwargs):
        payload = dict(
            username=username,
            password=password,
        )
        if 'verification_code' in kwargs.keys():
            payload['verification_code'] = kwargs['verification_code']
        response = self.session.post(json=payload)
        self.set_token(response.json()['token'])
        return response

    def api_login(self, username, password):
        return self.token_auth(username, password)

    def get_token(self, username, password):
        response = self.api_login(username, password)
        return response['token']

    @remote_service('/api/v4/processing/actions/{id}/requeue/')
    def requeue(self, processing_action_id, requeue_type=None, **kwargs):
        data = {}

        if requeue_type is not None:
            data['requeue_type'] = requeue_type

        return self.session.post(id=processing_action_id, data=data)

    @remote_service('/api/v4/processing/actions/{id}/cancel/')
    def cancel(self, processing_action_id, **kwargs):
        return self.session.post(id=processing_action_id)

    @remote_service('/api/v4/processing/actions/{id}/recalculate/')
    def recalculate(self, processing_action_id, **kwargs):
        return self.session.post(id=processing_action_id)

    @remote_service('/api/v4/processing/actions/{id}/')
    def processing_action_detail(self, processing_action_id, **kwargs):
        return self.session.get(id=processing_action_id)

    @remote_service('/api/v4/processing/actions/{id}/realogram/')
    def processing_action_realogram_detail(self, processing_action_id, **kwargs):
        return self.session.get(id=processing_action_id)

    @remote_service('/api/v4/processing/actions/{id}/')
    def processing_action_delete(self, processing_action_id, **kwargs):
        return self.session.delete(id=processing_action_id)

    @remote_service('/api/v4/processing/actions/{id}/send_oos_notification/')
    def send_oos_notification(self, processing_action_id, force=False, **kwargs):
        return self.session.post(id=processing_action_id, data={
            'force': force
        })

    @remote_service(
        '/api/v4/processing/actions/',
        request_uid_value=lambda **kwargs: kwargs['json'].pop('_request_uid', None))
    def create_processing_action(
        self, store_id, files, input_type='image',
        store_planogram=None,
        aisle=None, section=None,
        klt_json=None, lens_used=None,
        **kwargs
    ):
        """
        Create processing action for store using list of files
        :param int store_id:
        :param list<int> files:
        :param str input_type:
        :param int store_planogram:
        :param str aisle:
        :param str section:
        :param klt_json:
        :param lens_used:
        :param kwargs: all other fields that are sent to reference
        :return:
        """
        for f_ in files:
            assert isinstance(f_, int), "Should send IDs of uploaded files"

        assert input_type in ('video', 'image', 'keyframe'), \
            'Need to get video, image or keyframe, but %s supplied' % input_type

        data = {
            'store': store_id,
            'files': files,
            'input_type': input_type
        }
        if store_planogram:
            assert isinstance(store_planogram, int)
            data['store_planogram'] = store_planogram
        if aisle:
            assert isinstance(aisle, six.string_types)
            data['aisle'] = aisle
        if section:
            assert isinstance(section, six.string_types)
            data['section'] = section

        if klt_json:
            # encode KLT to string as it is accepted in API
            if isinstance(klt_json, dict):
                klt = json.dumps(klt_json)
            elif isinstance(klt_json, six.string_types):
                klt = klt_json
            else:
                # TODO: add path support and IO support
                raise ValueError('Unsupported value type for KLT.jsons')
            data['klt_json'] = klt

        if lens_used is not None:
            data['lens_used'] = lens_used

        for k, v in kwargs.items():
            data[k] = v

        return self.session.post(json=data)

    @remote_service('/api/v4/processing/upload/')
    def processing_upload(self, store_id, input_file, input_type='image', **kwargs):
        """Upload files that can be used for processing action creation"""
        assert isinstance(store_id, int), 'You need to specify store_id as int'
        assert input_type in (
            'image', 'video', 'keyframe'
        ), "File type should one of (image|video|keyframe) not %s" % input_type

        checksum = hash_file(input_file)
        input_file.seek(0)

        return self.session.post(data={
            'checksum': checksum,
            'input_type': input_type,
            'store': store_id
        }, files={
            'file': input_file
        })

    @remote_service('/api/v4/processing/upload/by-reference/')
    def processing_upload_by_reference(self, file_url, input_type='image', **kwargs):
        assert input_type in (
            'image', 'video', 'keyframe'
        ), "File type should one of (image|video|keyframe) not %s" % input_type

        return self.session.post(
            data={
                'input_type': input_type,
                'ref_url': file_url
            }
        )

    @remote_service('/api/v4/processing/upload/request/')
    def processing_upload_request(self, filename, input_type='image', **kwargs):
        return self.session.post(
            json={
                'filename': filename,
                'input_type': input_type
            }
        )

    @remote_service('/api/v4/processing/upload/request/{id}/finish/')
    def notify_processing_upload_finished(self, id_, **kwargs):
        return self.session.post(id=id_)

    @remote_service('/api/v4/export/products/')
    def export_products(self, products_filter=None, page=1, **kwargs):
        params = {
            'page': page,
            'page_size': 100,
        }
        if products_filter:
            params['filter'] = products_filter
        return PageResult(self.session.get(params=params))

    @remote_service('/api/v4/export/products/{product_id}/previews/')
    def get_product_previews(self, product_id, is_removed=None, page=1, **kwargs):
        params = {
            'page': page,
        }
        if is_removed is not None:
            assert isinstance(is_removed, bool)
            params['is_removed'] = is_removed

        return PageResult(self.session.get(
            product_id=product_id,
            params=params
        ))

    @remote_service('/api/v4/export/products/previews/', timeout=30000)
    def get_product_previews_bulk(self, product_id_list, **kwargs):
        filter_params = {'id': product_id_list}
        return self.session.post(data=filter_params)

    @remote_service('/api/v4/products/previews/')
    def upload_product_preview(self, upc, image_file, **kwargs):
        return self.session.post(data={
            'product_unique_id': upc,
        }, files={
            'image': image_file,
        })

    @remote_service('/api/v4/products/previews/delete/')
    def delete_product_previews(self, upc, **kwargs):
        return self.session.post(data={
            'product_unique_id': upc
        })

    @remote_service('/api/v4/products/search/')
    def get_product_info_by_upc(self, upc_list, **kwargs):
        if not all(upc.isdigit() for upc in upc_list):
            raise ValueError("Supplied non numeric code in list")

        return PageResult(self.session.post(json={
            'plu': upc_list
        }))

    @remote_service('/api/v4/product/previews/{preview_id}/add_feature_reference/')
    def set_product_preview_feature_id(self, preview_id, feature_id, facenet, **kwargs):
        return self.session.post(
            preview_id=preview_id,
            data={
                'feature_id': feature_id,
                'facenet': facenet,
            }
        )

    @remote_service('/api/v4/processing/actions/')
    def processing_action_list(self, store=None, status=None, aisle=None, section=None, page=1, page_size=100,
                               **kwargs):
        """Request processing action list"""

        def set_param(params, key, value):
            if value is not None:
                params[key] = value

        params = {
            'page': page,
            'page_size': page_size,
        }

        set_param(params, 'store', store)
        set_param(params, 'status', status)
        set_param(params, 'aisle', aisle)
        set_param(params, 'section', section)
        params.update(kwargs)

        data = self.session.get(params=params)
        return PageResult(data)

    @remote_service('api/v4/imports/planogram/assign/')
    def assign_planogram_with_file(self, assign_file, deactivate_old_planograms=False, **kwargs):

        file_io = None

        result = self.session.post(data={
            'deactivate_old_planograms': deactivate_old_planograms
        }, files={
            assign_file: file_io
        })

        file_io.close()
        return result

    @remote_service('api/v4/imports/planogram/')
    def import_planogram(
        self,
        planogram_file, title, description='',
        mappings=None,
        vertical_direction='top-to-bottom',
        horizontal_direction='left-to-right',
        horizontal_direction_shelf_bay='left-to-right',
        is_zig_zag=False,
        convert_upc=False,
        **kwargs
    ):
        """
        This will also close your file after transmission

        :param planogram_file: Planogram file as path, as StringIO/ByteIO, as URL
        :param str title: Planogram title, that you can use
        :param str description:
        :param dict mappings:
        :param str vertical_direction:
        :param str horizontal_direction:
        :param str horizontal_direction_shelf_bay:
        :param bool is_zig_zag:
        :param bool convert_upc: This flag will indicate that we need to convert what ever UPC to UPC-A format.
                                Please do not check if you provide EAN or other than UPC code.
        :return:
        """
        schema = self.session.options()
        post_schema = schema['actions']['POST']
        mapping_fields = post_schema['mappings']['children']
        option_fields = post_schema['options']['children']
        default_required_mappings = {key: key for key, value in mapping_fields.items() if value['required']}
        if mappings is None:
            mappings = default_required_mappings

        assert isinstance(mappings, dict)
        for key in default_required_mappings:
            if key not in mappings:
                raise AssertionError('You have not provided required key %s for API' % key)

        def get_choice_values(fields, key):
            return (choice['value'] for choice in fields[key]['choices'])

        assert vertical_direction in get_choice_values(option_fields, 'vertical_direction')
        assert horizontal_direction in get_choice_values(option_fields, 'horizontal_direction')
        assert horizontal_direction_shelf_bay in get_choice_values(option_fields, 'horizontal_direction_shelf_bay')
        assert isinstance(is_zig_zag, bool)
        assert isinstance(convert_upc, bool)
        assert isinstance(title, str), 'You need to specify title, instead %s with type %s was provided' % (
            title, type(title))
        assert isinstance(description, str), 'You need to specify description'

        file_io = accept_file(self, planogram_file)

        file_io.seek(0)

        response = self.session.post(json={
            'mappings': mappings,
            'options': {
                'vertical_direction': vertical_direction,
                'horizontal_direction': horizontal_direction,
                'horizontal_direction_shelf_bay': horizontal_direction_shelf_bay,
                'is_zig_zag': is_zig_zag,
                'convert_upc': convert_upc,
            },
            'title': title,
            'description': description,
        },
            files={
                'planogram_file': file_io
            })
        file_io.close()

        return response

    @remote_service('api/v4/imports/planogram-assign-file/')
    def assign_planogram(self, assign_file, deactivate=False, **kwargs):
        """
        Uploads an assign planogram file to retailer. Be careful to upload it.
        :param assign_file: file-like object
        :param bool deactivate: flag to deactivate old existing store planograms
        :return:
        """
        assert isinstance(deactivate, bool)
        file_io = accept_file(self, assign_file)
        file_io.seek(0)

        response = self.session.post(data={
            'deactivate_old_planogram': deactivate
        }, files={
            'assign_file': file_io
        })

        file_io.close()
        return response

    @remote_service('api/v4/store_aisles/{store_id}')
    def get_store_aisles(self, store_id, **kwargs):
        return self.session.get(store_id=store_id)

    @remote_service('api/v4/stores/')
    def get_stores(self, **kwargs):
        return self.session.get()

    @remote_service('api/v4/processing_aisles/{processing_id}/')
    def get_processing_aisles(self, processing_id, **kwargs):
        return self.session.get(processing_id=processing_id)

    @remote_service('api/v4/users/')
    def user_list(self, **kwargs):
        return self.session.get()

    @remote_service('api/v4/users/{username}/subscriptions/')
    def user_subscriptions(self, username, **kwargs):
        return self.session.get(username=username)

    @remote_service('api/v4/users/{username}/subscriptions/')
    def user_subscriptions_create(self, username, store, aisle, section, **kwargs):
        return self.session.post(
            username=username,
            data={
                'store': store,
                'aisle': aisle,
                'section': section,
            }
        )

    @remote_service('api/v1/master-data/file-upload/')
    def v1_upload_file(self, file, **kwargs):
        return self.session.post(
            data={
                'description': 'preview upload from SDK',
            },
            files={
                'file': file
            }
        )

    @remote_service('api/v1/master-data/products/{product_id}/images/')
    def v1_upload_preview(self, product_id, image_id, **kwargs):
        return self.session.post(
            product_id=product_id,
            json={
                'image': image_id
            }, content_type='application/json')

    @remote_service('api/v4/processing/actions/{id}/spacial')
    def get_spacial_data(self, scan_id, **kwargs):
        """Can yield permission error. Internal usage intended"""
        return self.session.get(id=scan_id)

    @remote_service('api/v4/processing/actions/export-to-dataset/')
    def export_to_dataset(self, scan_ids, batch_size=5, **kwargs):
        return self.session.post(json={
            'scans': sorted(list(set(scan_ids))),
            'batch_size': batch_size,
        })

    @remote_service('/api/v1/rebotics/rpc/export-feature-vector/')
    def feature_vectors_export(self):
        return FeatureVectorFlow(self, self.session)

    @remote_service('/api/v1/realograms/scan-batch/bin/')
    def create_scan_batch_bin(self, items):
        # TODO: move to pydantic
        required_keys = {
            "imageName": str,
            "timestamp": str,
            "sensorName": str,
            "clubId": str,
            "annotationVersion": int,
            "locationLabels": {
                "area": (str, False),
                "aisle": (str, False),
                "section": (str, False),
            },
            "pose": {
                "x": float,
                "y": float,
                "theta": (float, False)
            },
            "locationId": (str, False),
            "href": str
        }

        def _validate_field(obj, key, conf):
            value = obj.get(key)
            if isinstance(value, dict):
                return _validate_field(value, key, conf[key])

            required_ = True
            if isinstance(conf, tuple):
                type_, required_ = conf
            else:
                type_ = conf

            if value is None:
                if required_:
                    raise ValueError("Field {} is required".format(key))
            else:
                if isinstance(value, type_):
                    raise ValueError("Field {} does not match required type".format(key, str(type_)))

        for entry in items:
            if not isinstance(entry, dict):
                raise ValueError("Entry should be dict")
            for expected_key, conf in required_keys.items():
                _validate_field(entry, expected_key, conf)

        return self.session.post(json=items)
