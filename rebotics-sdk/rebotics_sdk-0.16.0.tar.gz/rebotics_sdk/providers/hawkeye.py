import io
import typing

from .base import ReboticsBaseProvider, remote_service, PageResult


class HawkeyeProvider(ReboticsBaseProvider):

    @remote_service('/api-token-auth/', raw=True)
    def token_auth(self, username, password, **kwargs):
        response = self.session.post(data={
            'username': username,
            'password': password
        })
        self.set_token(response.json()['token'])
        return response

    @remote_service('/api/v1/camera/heartbeats/')
    def save_camera_heartbeat(self, shelf_camera, battery_status, free_storage, used_storage):
        return self.session.post(json={
            "shelf_camera": shelf_camera,
            "battery_status": battery_status,
            "free_storage": free_storage,
            "used_storage": used_storage
        })

    @remote_service('/api/v1/camera/camera-actions/')
    def save_camera_action(self, action_type, status_type, payload, shelf_camera):
        return self.session.post(json={
            "action_type": action_type,
            "status_type": status_type,
            "payload": payload,
            "shelf_camera": shelf_camera
        })

    @remote_service('/api/v1/camera/camera-actions/')
    def get_camera_actions(self):
        return self.session.get()

    @remote_service('/api/v1/camera/retailer/')
    def save_retailer(self, codename, token):
        return self.session.post(json={
            "retailer": codename,
            "token": token
        })

    @remote_service('/api/v1/camera/fixtures/')
    def save_fixture(self, retailer, store_id, aisle, section):
        return self.session.post(
            json={
                "store_id": store_id,
                "aisle": aisle,
                "section": section,
                "retailer": retailer
            }
        )

    @remote_service('/api/v1/camera/fixtures/{id}')
    def delete_fixture(self, pk):
        return self.session.delete(id=pk)

    @remote_service('/api/v1/camera/fixtures/')
    def get_fixtures(self):
        return self.session.get()

    @remote_service('/api/v1/camera/shelf-cameras/')
    def create_shelf_camera(self, camera_id, added_by, fixture=None):
        data = {
            "camera_id": camera_id,
            "added_by": added_by,
        }
        if fixture is not None:
            data["fixture"] = fixture
        return self.session.post(json=data)

    @remote_service('/api/v1/camera/shelf-cameras/')
    def get_shelf_cameras(self):
        return self.session.get()

    @remote_service('/api/v1/camera/shelf-cameras/{id}/')
    def get_shelf_camera(self, id_):
        return self.session.get(id=id_)

    @remote_service('/api/v1/camera/shelf-cameras/{id}/')
    def update_shelf_camera(
        self,
        id_,
        camera_id: str = None,
        added_by: int = None,
        fixture: int = None,
        perspective_warp: typing.List[typing.List[int]] = None,
        force_null=False
    ):
        data_to_update = {
            "camera_id": camera_id,
            "added_by": added_by,
            "fixture": fixture,
            "perspective_warp": perspective_warp
        }

        return self.session.patch(
            id=id_,
            json={k: v for k, v in data_to_update.items() if not force_null and v is not None}
        )

    @remote_service('/api/v1/fetcher/{camera_id}/')
    def save_capture(self, camera, file_key, bucket_name):
        return self.session.post(
            camera_id=camera,
            json={
                "file_key": file_key,
                "bucket_name": bucket_name
            })

    @remote_service('/api/v1/camera/mac-address/search/')
    def search_camera_by_mac(self, mac_address):
        assert ":" in mac_address, "Mac address should be separated by : (colon)"
        return self.session.post(json={
            'mac_address': mac_address
        })

    @remote_service('/api/v1/camera/mac-address/')
    def create_mac_address_link(self, mac_address, vendor_secret, rebotics_secret):
        assert ":" in mac_address, "Mac address should be separated by : (colon)"
        return self.session.post(json={
            'mac_address': mac_address,
            'vendor_secret': vendor_secret,
            'rebotics_secret': rebotics_secret,
        })

    @remote_service('/api/v1/camera/mac-address/{id}/')
    def update_mac_address_link(self, id_, mac_address, vendor_secret, rebotics_secret):
        assert ":" in mac_address, "Mac address should be separated by : (colon)"
        assert isinstance(id_, int), "Link ID should be integer, use search by mac-address to determine Link ID"
        return self.session.patch(id=id_, json={
            'mac_address': mac_address,
            'vendor_secret': vendor_secret,
            'rebotics_secret': rebotics_secret,
        })

    @remote_service('/api/v1/camera/mac-address/{id}/', raw=True)
    def delete_mac_address_link(self, id_):
        response = self.session.delete(id=id_)
        response.raise_for_status()

    @remote_service('/api/v1/camera/shelf-cameras/{shelf_camera_id}/captures/{capture_id}/warped/',
                    raw=True, stream=True, allow_redirects=True)
    def get_warped_image(self, shelf_camera_id, capture_id, polygon):
        """
        Return warped image with given values.
        Return value is io.BytesIO
        """
        assert len(polygon) == 4, "There should be 4 points"
        assert all(len(coordinate) == 2 for coordinate in polygon), "They should be in format [x, y]"
        params = {
            'polygon': ','.join(
                str(point)
                for coordinate in polygon
                for point in coordinate
            )
        }
        response = self.session.get(
            params=params,
            shelf_camera_id=shelf_camera_id,
            capture_id=capture_id,
            stream=True
        )
        response.raise_for_status()
        fp = io.BytesIO()
        for chunk in response.iter_content(chunk_size=1024):
            fp.write(chunk)
        fp.seek(0)
        return fp

    @remote_service('/api/v1/camera/shelf-cameras/{shelf_camera_id}/captures/')
    def get_shelf_camera_captures(self, shelf_camera_id, page=None):
        """Get shelf camera captures"""
        if page is None:
            page = 1
        params = {
            'page': page,
        }
        return PageResult(
            self.session.get(shelf_camera_id=shelf_camera_id, params=params)
        )
