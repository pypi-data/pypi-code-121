import os
import socket
import time
from datetime import datetime

import json
from threading import Thread

import paho.mqtt.client as mqttClient
import yaml
from ndu_gate_camera.utility import constants, ndu_utility
from pathlib import Path
from threading import Lock
import requests
import shutil


class ResultHandlerMqtt:
    '''
        Cihaz verilerinin NDU platformuna MQTT APİ üzerinden gönderilmesi
    '''

    def __init__(self, access_token, mqtt_obj, config_file, plate_service_url, use_platform):
        host = mqtt_obj.get("host")
        self.host = host
        self.port = mqtt_obj.get("port")
        self.connected_devices = {}
        self.connected = False
        self.access_token = access_token
        self.client = mqttClient.Client()
        self.client.username_pw_set(access_token)
        self.config_file = config_file
        self.platform = use_platform
        if use_platform:
            self.client.on_message = self.on_message
            self.client.on_subscribe = self.on_subscribe
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.disconnected_data = []
        self.plate_service_url = plate_service_url
        self.frame = {}
        self.frames_path = ""
        self.restart_required = False
        self.save_lock = Lock()
        self.frame_lock = Lock()
        self.url = ""
        self.http_url = mqtt_obj.get("http_url", "api/v1/")
        ndu_utility.NDUUtility.host = self.host
        # Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
        try:
            self.client.connect(host, mqtt_obj.get("port"), 5)
            self.client.loop_start()
            self.connected = True
            if use_platform:
                self.client.subscribe("v1/devices/me/attributes/response/+")
                self.client.publish("v1/devices/me/attributes/request/1", '{"sharedKeys":"conf"}')
                self.client.subscribe("v1/devices/me/attributes")
        except socket.error:
            print("can not connect mqtt broker!")
            port = mqtt_obj.get("port")
            self.try_to_connect(host, port)

    def set_frame(self, device_name, frame):
        with self.frame_lock:
            if device_name not in self.frame and self.platform:
                self.frame.update({device_name: frame})
                self.post_frame('send_frame-' + device_name)
            else:
                self.frame.update({device_name: frame})

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print('subscribed')

    def on_message(self, client, userdata, message):
        print("message received  ", str(message.payload.decode("utf-8")), \
              "topic", message.topic, "retained ", message.retain)

        obj = json.loads(message.payload.decode("utf-8"))
        runner_conf = self.check_configuration(obj)
        if runner_conf is not None:
            self.update_runner_configuration(runner_conf, obj)
        f = self.check_frame(obj)
        if f is not None and self.frame:
            self.post_frame(f)

        if 'shared' in obj:
            obj = obj['shared']

        if 'device' in obj:
            self.update_camera_configuration(obj)

        if constants.CONFIGURATION_KEY in obj:
            curr = yaml.safe_load(open(self.config_file))
            obj = self.remove_custom_runners(obj)
            if curr != obj[constants.CONFIGURATION_KEY] and len(obj[constants.CONFIGURATION_KEY]['instances']) > 0:
                with open(self.config_file, 'w',
                          encoding='utf-8') as f:
                    yaml.dump(obj[constants.CONFIGURATION_KEY], f, allow_unicode=True)
                    self.restart_required = True
                    self.dispose()

        if message.retain == 1:
            print("This is a retained message")

    def remove_custom_runners(self, obj):
        keys_to_remove = []
        for instance in obj[constants.CONFIGURATION_KEY]['instances']:
            for idx, runner in enumerate(instance['runners']):
                if runner['configuration'].startswith('custom'):
                    print(instance['runners'][idx])
                    keys_to_remove.append(instance['runners'][idx])

        for key in keys_to_remove:
            for instance in obj[constants.CONFIGURATION_KEY]['instances']:
                for idx, runner in enumerate(instance['runners']):
                    if runner == key:
                        del instance['runners'][idx]

        return obj

    def check_frame(self, obj):
        # for k in obj:
        #     if constants.SEND_FRAME in k:
        #         return k
        if 'data' in obj.keys():
            for k in obj['data']:
                if constants.SEND_FRAME in k:
                    return k

    def get_restart_required(self):
        return self.restart_required

    def check_configuration(self, obj):
        for k in obj:
            if '.json' in k:
                return k
        return None

    def update_camera_configuration(self, obj):
        try:
            if list(obj['data'].keys())[0].endswith('.json') and list(obj['data'].keys())[0].startswith(
                    'custom') is False:
                runner_conf = list(obj['data'].keys())[0]
                data = obj['data'][runner_conf]
                config_dir = Path(self.config_file).parent
                with open(os.path.join(config_dir, runner_conf), 'r+') as file:
                    d = json.load(file)
                    if 'object_counter' in runner_conf:
                        d['gates'] = data['gates']
                        for value in d['classes'].keys():
                            s = value
                        d['classes'][s] = data['classes']
                    elif 'intersector' in runner_conf:
                        d['groups'][list(d['groups'])[0]]['obj_detection']['ground'] = data['ground']
                        d['groups'][list(d['groups'])[0]]['obj_detection']['dist'] = data['dist']
                        d['groups'][list(d['groups'])[0]]['obj_detection']['rects'][0]['class_names'] = data[
                            'class_names']
                    elif 'objects_in_area' in runner_conf:
                        d['areas'] = data['areas']
                        d['classes'] = data['classes']
                    elif 'point_occupied' in runner_conf:
                        d['points'] = data

                    with open(os.path.join(config_dir, runner_conf), 'w') as file:
                        print('File opened')
                        json.dump(d, file, indent=4)
                        self.restart_required = True
                        self.dispose()
        except Exception as e:
            print(e)
            self.create_default_conf(runner_conf)
            self.update_camera_configuration(obj)

    def update_runner_configuration(self, runner_conf, obj):
        data = obj[runner_conf]
        config_dir = Path(self.config_file).parent
        try:
            with open(os.path.join(config_dir, runner_conf), 'r+') as file:
                d = json.load(file)
                if runner_conf.startswith('object_counter'):
                    d['gates'] = data['gates']
                    for value in d['classes'].keys():
                        s = value
                    d['classes'][s] = data['classes']
                elif runner_conf.startswith('intersector_'):
                    d['groups'][list(d['groups'])[0]]['obj_detection']['ground'] = data['ground']
                    d['groups'][list(d['groups'])[0]]['obj_detection']['dist'] = data['dist']
                    d['groups'][list(d['groups'])[0]]['obj_detection']['rects'][0]['class_names'] = data['class_names']
                elif runner_conf.startswith('objects_in_area'):
                    d['areas'] = data['areas']
                    d['classes'] = data['classes']
                elif runner_conf.startswith('point_occupied'):
                    d['points'] = data

                with open(os.path.join(config_dir, runner_conf), 'w') as file:
                    print('File opened')
                    json.dump(d, file, indent=4)
                    self.restart_required = True
                    self.dispose()

        except Exception as e:
            print(e)
            self.create_default_conf(runner_conf)
            self.update_runner_configuration(runner_conf, obj)

    def create_default_conf(self, runner_conf):
        config_path = os.path.abspath(self.config_file + "/../")
        os.chdir(config_path)
        files = os.listdir()
        os.chdir(config_path)
        for item in files:
            extension = item.split('.')[-1]
            item = item.split('.')[0]
            if item in runner_conf and extension == 'json':
                try:
                    shutil.copy(os.path.join(config_path, item + '.' + extension),
                                os.path.join(config_path, runner_conf))
                except shutil.SameFileError:
                    print("Source and destination represents the same file.")

    def post_frame(self, f):
        device_name = f[len(constants.SEND_FRAME) + 1:]
        headers = {
            'Content-Type': 'application/json',
        }
        # self.frame_lock.acquire()
        label = ''.join(device_name.split())
        try:
            data = '{frame_' + label + ': "' + self.frame[device_name] + '"}'
            # self.frame_lock.release()
            # mqtt_data = {
            #     device_name: data
            # }
            # self.client.publish('v1/gateway/attributes', json.dumps(mqtt_data), 1)
            response = requests.post('http://' + self.host + '/api/v1/' + self.access_token + '/attributes',
                                     headers=headers, data=data)
        except Exception as e:
            print(e)

    def find_runners(self, json, device, new_runners):
        instances = json['instances']
        for instance in instances:
            if instance['source']['device'] == device:
                instance['runners'] = new_runners
        return instances

    def try_to_connect(self, host, port):
        try:
            self.client.connect(host, port, 60)
            self.client.loop_start()
        except socket.error:
            import time
            print("can not connect mqtt broker, trying again in 15 seconds")
            time.sleep(15)
            self.try_to_connect(self.host, self.port)

    def on_connect(self, client, userdata, flags, rc):
        print('connected')
        self.connected = True
        self.disconnected_data = self.load_data(constants.LOCAL_RESULTS_PATH)

        if len(self.disconnected_data) > 0:
            self.publish_historic_data(self.disconnected_data)
            self.disconnected_data = []
            self.clear_file(constants.LOCAL_RESULTS_PATH)

    def clear_file(self, filename):
        open(filename, 'w').close()

    def publish_historic_data(self, results):
        for result in results:
            self.client.publish('v1/gateway/telemetry', json.dumps(result), 1)

    def on_disconnect(self, client, userdata, rc=0):
        print('disconnected')
        self.connected = False

    def send_connect_request(self, device_name):
        mqtt_data = {"device": device_name}
        self.client.publish('v1/gateway/connect', json.dumps(mqtt_data), 1)
        self.connected_devices[device_name] = True

    def send_disconnect_request(self, device_name):
        mqtt_data = {"device": device_name}
        self.client.publish('v1/gateway/disconnect', json.dumps(mqtt_data), 1)
        self.connected_devices.pop(device_name)

    def save_result(self, results, device=None, runner_name=None, data_type='telemetry'):
        with self.save_lock:
            if self.connected is True:
                if self.connected_devices.get(device) is None:
                    self.send_connect_request(device)

                if data_type == 'telemetry':
                    self.send_telemetry(device, results)
                elif data_type == 'attribute':
                    self.send_attribute(device, results)
            else:
                self.store_local(results, constants.LOCAL_RESULTS_PATH, device)

    def store_local(self, results, filename, device):
        if (os.path.getsize(filename)) > constants.LOCAL_RESULT_LIMIT_BYTE:
            self.clear_file(filename)
            return

        file = open(filename, 'a')
        mqtt_data = {
            device: []
        }
        for result in results:
            if result is None:
                continue
            data = result.get(constants.RESULT_KEY_DATA, None)

            if data is None:
                continue

            single_data = {}
            single_data['ts'] = round(time.time()) * 1000
            single_data['values'] = {}
            for key in data:
                if data[key] is not None:
                    single_data['values'][key] = data[key]
            # mqtt_data[device].append(time.time())
            mqtt_data[device].append(single_data)
            file.write(json.dumps(mqtt_data))
            file.write("\n")
        file.close()

    def load_data(self, filename):
        result_list = []
        try:
            with open(filename) as f:
                for line in f:
                    # get json object
                    json_object = json.loads(line)
                    # add json object to list
                    result_list.append(json_object)
        except:
            f = open(filename, 'w+')
        return result_list

    def save_frames_locally(self, base64frame, device):
        import base64, datetime
        from os import path
        from ndu_gate_camera.utility import image_helper
        device = device.replace(" ", "-")
        device = device.replace("_", "-")
        if self.frames_path == "":
            config = yaml.safe_load(open(self.config_file))
            if config.get("frames_path") is None:
                return
            self.frames_path = config["frames_path"]
            image_helper.set_frames_path(self.frames_path)

        if image_helper.get_size(self.frames_path) > 5000000000:  # 5000000000
            dir_list = next(os.walk(self.frames_path))[1]
            dir_list.sort()
            shutil.rmtree(self.frames_path + path.sep + dir_list[0])
        # check frame number, if > 10000, create video
        elif image_helper.get_frames_number() > 1000:
            image_helper.create_video()
        else:
            date = str(datetime.datetime.now().strftime("%Y-%m-%d"))

            if not os.path.exists(self.frames_path + path.sep + date):
                os.makedirs(self.frames_path + path.sep + date)

            if not os.path.exists(self.frames_path + path.sep + date + path.sep + device):
                os.makedirs(self.frames_path + path.sep + date + path.sep + device)

            with open(os.path.join(self.frames_path + path.sep + date + path.sep + device, device + '_' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(":", "-") + image_helper.frame_extension), "wb") as fh:
                fh.write(base64.b64decode(base64frame))
                fh.close()

    def send_frame_http(self, frame, device):
        headers = {
            'Content-Type': 'application/json',
        }
        device = device.replace(" ", "_")
        data = '{frame_' + device + ': "' + frame + '"}'

        try:
            self.save_frames_locally(frame, device)
            response = requests.post(self.http_url + self.access_token + "/attributes",
                                     headers=headers, data=data)
            # print(response)
        except Exception as e:
            print(e)

    def send_telemetry(self, device, results):
        try:
            mqtt_data = {
                device: []
            }
            # if mqtt_data.get(device) is None:
            #     mqtt_data['device'] = 'device'

            for result in results:
                if result is None:
                    continue
                data = result.get(constants.RESULT_KEY_DATA, None)

                if data is None:
                    continue

                single_data = {}
                for key in data:
                    if data[key] is not None:
                        if key == "frame":
                            self.send_frame_http(data[key], device)
                        else:
                            single_data[key] = data[key]

                mqtt_data[device].append(single_data)
                if self.plate_service_url is not None:
                    try:
                        now = datetime.now()
                        plate_res = {
                            'access_token': self.access_token,
                            'name': device,
                            'vehicle_type': data['vehicle_type'],
                            'licencePlate': data['plate'],
                            'enter': data['enter'],
                            'timestamp': now
                        }
                        print(plate_res)
                        r = requests.get('https://api.github.com/')
                        requests.post(self.plate_service_url, plate_res)
                        print(r.status_code)
                    except:
                        pass

            if not len(mqtt_data[device]) == 0:
                self.client.publish('v1/gateway/telemetry', json.dumps(mqtt_data), 1)

        except socket.error:
            print('Cannot send data due to connection lost')

        except KeyError:
            print('Exception while saving result, key error')

    def send_frame(self, device, data):
        try:
            mqtt_data = {
                device: {}
            }

            for key in data:
                if data[key] is not None:
                    mqtt_data[device][key] = data[key]

            if not len(mqtt_data[device]) == 0:
                self.client.publish('v1/gateway/attributes', json.dumps(mqtt_data), 1)
        except KeyError:
            print('Exception while saving frame, key error')

    def send_attribute(self, device, results):
        try:
            mqtt_data = {
                device: {}
            }

            for result in results:
                if result is None:
                    continue
                data = result.get(constants.RESULT_KEY_DATA, None)

                if data is None:
                    continue

                for key in data:
                    if data[key] is not None:
                        mqtt_data[device][key] = data[key]

            if not len(mqtt_data[device]) == 0:
                self.client.publish('v1/gateway/attributes', json.dumps(mqtt_data), 1)
        except KeyError:
            print('Exception while saving result, key error')

    def dispose(self):
        self.client.disconnect()
        pass
