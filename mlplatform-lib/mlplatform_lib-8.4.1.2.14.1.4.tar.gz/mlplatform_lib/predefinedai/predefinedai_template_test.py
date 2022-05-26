from mlplatform_lib.predefinedai.pre_check_predefinedai import PreCheckPredefinedAI

import json
import requests
from time import sleep
import uuid
import yaml


class PredefinedAITemplateTest:
    def __init__(self, server_config_path: str, image_config_path: str):
        # replace test params
        server_config = yaml.safe_load(open(server_config_path))
        self.pre_check = PreCheckPredefinedAI(server_config_path)
        self.pre_check.run()

        self.mlplatform_addr = server_config["mlplatform_addr"]
        self.image_config = yaml.safe_load(open(image_config_path))
        self.experiment_id = None

    def _print_train_logs(self, experiment_id, train_id):
        self.pre_check._print_header("train log start")
        log_url = f"{self.mlplatform_addr}/experiments/{experiment_id}/trains/{train_id}/logs/predefinedai"
        res = requests.get(log_url, headers=self.pre_check.mlplatform_request_header)
        logs = json.loads(res.text)
        for log in logs:
            print(f"##########{log['name']}##########")
            print(log["log"])
            print("\n")

    """
    def _print_inference_logs(self, experiment_id, inference_id):
        self.pre_check._print_header("inference log start")
        log_url = self.mlplatform_addr + "/predefinedai/v2/log/inference"
        log_url += "?experiment_id=" + str(experiment_id)
        log_url += "&inference_id=" + str(inference_id)
        res = requests.get(log_url, headers=self.request_header)
        print(res.text)
        logs = json.loads(res.text)
        for log in logs:
            print(f"##########{log['name']}##########")
            print(log["log"])
            print("\n")
    """

    def _experiment(self):
        self.pre_check._print_header("predefinedai template experiment start")

        experiment_url = f"{self.pre_check.mlplatform_addr}/experiments"
        model_name = self.image_config["train"]["model"]
        random_generated_experiment_name = f"{model_name}_{str(uuid.uuid4())}"

        create_experiment_data = {
            "name": random_generated_experiment_name,
            "experimentType": "predefinedai",
            "pvcSize": 10,
            "description": f"{random_generated_experiment_name} description.",
            "doId": self.pre_check.train_do_id,
            "taskType": model_name,
        }

        print(f"experiment_name: {random_generated_experiment_name}")
        print(
            "send create experiment request to mlplatform server. After creating experiments,"
            + "training will start."
        )
        res = requests.post(
            experiment_url, json=create_experiment_data, headers=self.pre_check.mlplatform_request_header
        )
        if res.status_code != 200:
            raise Exception(f"create experiment failed.\nstatus_code: {res.status_code}\nreason: {res.text}")
        else:
            # set experiment id for retraining
            self.experiment_id = json.loads(res.text)["id"]
            print("create experiment succeeded.\n")

    def _train(self):
        self.pre_check._print_header("predefinedai template train start")

        train_url = f"{self.mlplatform_addr}/experiments/{self.experiment_id}/trains"
        create_train_data = {
            "experimentType": "predefinedai",
            "workflow": {
                "maxCpuSize": 1,
                "maxMemorySize": 1,
                "maxGpuSize": 0,
                "description": "workflow test",
            },
            "args": self.image_config["train"]["template"]["args"],
            "envs": self.image_config["train"]["template"]["envs"],
        }

        res = requests.post(
            train_url, json=create_train_data, headers=self.pre_check.mlplatform_request_header
        )
        if res.status_code != 200:
            raise Exception(f"create train failed. reason: {res.text}")
        else:
            print("wait until train finished.")

            train_id = res["id"]
            train_url_get = f"{train_url}/{train_id}"
            while True:
                res = requests.get(train_url_get, headers=self.pre_check.mlplatform_request_header)

                if res["workflow"]["status"] == "failed":
                    self._print_train_logs(self.experiment_id, train_id)
                    raise Exception("train failed.")
                elif res["workflow"]["status"] == "Succeeded":
                    break
                sleep(5)
            print("train succeeded.\n")

    """
    # 재학습은 내부적으로 학습 시에 사용했던 DO와 같은 DO를 사용하도록 되어 있습니다.
    # 따라서 do_id를 전송하지 않습니다.
    def _retrain(self):
        self.pre_check._print_header("retrain start")
        experiment_url = self.mlplatform_addr + "/predefinedai/v2/experiments"
        retrain_experiment_data = self.image_config["retrain"]
        retrain_experiment_data["experiment_id"] = self.experiment_id
        # retrain_experiment_data = {
        #    "experiment_id": self.experiment_id,
        # }
        # 덮어쓰기 가능한 목록
        # retrain_experiment_data = {
        #    "experiment_id": self.experiment_id,
        #    "pipeline_image_info": {
        #        "cpu": "2",
        #        "memory": "2Gi",
        #        "gpu": "0",
        #        "args": {
        #            "seed": 6
        #        },
        #        "envs": {}
        #    }
        # }
        print("send retrain experiment request to automl server.")
        res = requests.put(
            experiment_url, json=retrain_experiment_data, headers=self.request_header
        )
        if res.status_code != 200:
            raise Exception(f"retrain failed. reason: {res.text}")
        else:
            print("wait until retrain finished.")

            experiment_url_get = (
                experiment_url + "?experiment_id=" + str(self.experiment_id)
            )
            while True:
                res = requests.get(experiment_url_get, headers=self.request_header)
                if res.status_code != 200:
                    raise Exception(f"Get experiment info failed. " f"reason: {res.text}",)

                experiment_info = json.loads(res.text)
                current_workflow_infos = experiment_info["workflows"][-1]
                if current_workflow_infos["status"] == "Failed":
                    self._print_train_logs(self.experiment_id, current_workflow_infos["id"])
                    raise Exception("retrain failed.")
                elif current_workflow_infos["status"] == "Succeeded":
                    # set workflow info for next inference
                    self.workflow_id = current_workflow_infos["id"]
                    break
                sleep(5)
            print("retrain succeeded.\n")

    def _inference(self):
        self.pre_check._print_header("inference start")
        inference_url = self.mlplatform_addr + "/predefinedai/v2/inferenceservice"
        inference_data = self.image_config["inference"]
        inference_data["experiment_id"] = self.experiment_id
        inference_data["workflow_id"] = self.workflow_id
        inference_data["input_do_id"] = self.inference_do_id
        inference_data["is_truncated"] = False
        # inference_data = {
        #    "experiment_id": self.experiment_id,
        #    "workflow_id": self.workflow_id,
        #    "input_do_id": self.inference_do_id,
        #    "is_truncated": True,
        # }
        # 덮어쓰기 가능한 목록
        # inference_data = {
        #    "experiment_id": self.experiment_id,
        #    "workflow_id": self.workflow_id,
        #    "input_do_id": self.inference_do_id,
        #    "is_truncated": True,
        #    "pipeline_image_info": {
        #        "cpu": "2",
        #        "memory": "2Gi",
        #        "gpu": "0",
        #        "args": {
        #            "seed": 7
        #        },
        #        "envs": {}
        #    }
        # }
        print("send inference request to automl server.")
        res = requests.post(inference_url, json=inference_data, headers=self.request_header)
        if res.status_code != 200:
            raise Exception(f"inference failed. reason: {res.text}")
        else:
            print("wait until inference finished.")

            self.inference_id = json.loads(res.text)["inference_id"]
            inference_url_get = (
                inference_url
                + "?experiment_id="
                + str(self.experiment_id)
                + "&inference_id="
                + str(self.inference_id)
            )
            while True:
                res = requests.get(inference_url_get, headers=self.request_header)
                if res.status_code != 200:
                    raise Exception(f"Get inference info failed. " f"reason: {res.text}")

                res_json = json.loads(res.text)
                inference_status = res_json["inference_status"]
                if inference_status == "Failed":
                    self._print_inference_logs(self.experiment_id, res_json["inference_id"])
                    raise Exception("inference failed.")
                elif inference_status == "Finished":
                    break
                sleep(5)
            print("inference succeeded.\n")

    def _inference_download(self):
        self.pre_check._print_header("inference download start")
        inference_download_url = self.mlplatform_addr + "/predefinedai/v2/inferenceservice"
        inference_download_url += "?action=Download"
        inference_download_url += "&experiment_id=" + str(self.experiment_id)
        inference_download_url += "&inference_id=" + str(self.inference_id)
        res = requests.get(inference_download_url, headers=self.request_header, stream=True)
        if res.status_code == 200:
            print("inference download succeeded.\n")
        else:
            raise Exception(f"inference download failed. reason: {res.text}")

    def _serving(self):
        self.pre_check._print_header("serving start")
        serving_url = self.mlplatform_addr + "/predefinedai/v2/serving"
        # kfserving works based on knative.
        # and knative uses docker image digest instead of tag
        # refer. https://knative.dev/docs/serving/tag-resolution/
        # https://docs.google.com/presentation/d/e/2PACX-1vTgyp2lGDsLr_bohx3Ym_2mrTcMoFfzzd6jocUXdmWQFdXydltnraDMoLxvEe6WY9pNPpUUvM-geJ-g/pub?resourcekey=0-FH5lN4C2sbURc_ds8XRHeA&slide=id.p
        # docker image digest can find using docker pull command.
        # --example--
        # user> docker pull 127.0.0.1:5000/hyperdata/sentimentanalysis_base:20210322_v1
        # 20210322_v1: Pulling from hyperdata/sentimentanalysis_base
        # Digest: sha256:40618baabd44864647460d43721dbf548a43e5b20406e66d58fafd11b3ac02c3
        # Status: Image is up to date for 127.0.0.1:5000/hyperdata/sentimentanalysis_base:20210322_v1
        # 127.0.0.1:5000/hyperdata/sentimentanalysis_base:2021-0322_v1
        serving_data = self.image_config["serving"]
        serving_data["experiment_id"] = self.experiment_id
        serving_data["workflow_id"] = self.workflow_id
        # serving_data = {
        #    "experiment_id": self.experiment_id,
        #    "workflow_id": self.workflow_id,
        # }
        # 덮어쓰기 가능한 목록
        # serving_data = {
        #    "experiment_id": self.experiment_id,
        #    "workflow_id": self.workflow_id,
        #    "serving_image_info": {
        #        "requests_cpu": "1",
        #        "limits_cpu": "2",
        #        "requests_memory": "1Gi",
        #        "limits_memory": "2Gi",
        #        "requests_gpu": "0",
        #        "limits_gpu": "0",
        #        "min_replicas": "1",
        #        "max_replicas": "1",
        #        "args": {},
        #        "envs": {},
        #    },
        # }
        print("send start serving server request to mlplatform server.")
        res = requests.post(serving_url, json=serving_data, headers=self.request_header)
        if res.status_code != 200:
            raise Exception(f"serving failed. reason: {res.text}")
        else:
            print("wait until serving server is start.")
            while True:
                serving_url_get = (
                    serving_url
                    + "?experiment_id="
                    + str(self.experiment_id)
                    + "&workflow_id="
                    + str(self.workflow_id)
                )
                res = requests.get(serving_url_get, headers=self.request_header)
                if res.status_code not in [200, 503, 404]:
                    raise Exception(f"Get serving info failed. " f"reason: {res.text}")

                res_json = json.loads(res.text)
                if res_json["serve_status"] == "Possible":
                    service_host_name = res_json["service_host_name"]
                    url = res_json["url"]

                    # ref. https://github.com/kubeflow/kfserving/tree/release-0.4#test-kfserving-installation
                    # kfserving request header
                    headers = {"Host": service_host_name}
                    # kfserving input

                    result = self.pre_check.hyperdata_client.get_do_samples(
                        self.pre_check.auth, self.inference_do_id, 10
                    )
                    result_data = json.loads(result.data["dto"]["tableString"])
                    response_data = {
                        "columns": list(result_data[0].keys()),
                        "rows": [],
                    }
                    for data_dict in result_data:
                        response_data["rows"].append(
                            list(map(str, list(data_dict.values())))
                        )

                    request_json = {"instances": []}
                    for row in response_data["rows"]:
                        instance = {}
                        for idx, val in enumerate(row):
                            instance[response_data["columns"][idx]] = val
                        request_json["instances"].append(instance)
                    print(
                        "In test, serving uses inference input data as serving input data."
                    )
                    print("serving_input_data: ", request_json)
                    try_cnt = 0
                    while try_cnt < 10:
                        res = requests.post(
                            url, headers=headers, data=json.dumps(request_json)
                        )
                        if res.status_code == 200:
                            print("serving_output_data: ", res.text)
                            print("serving succeeded.")
                            return
                        sleep(5)
                        try_cnt += 1
                    raise Exception(f"serving failed. reason: {res.text}")
                sleep(5)
    """

    def _delete_experiment(self):
        print("unittest finished.")
        if self.experiment_id is not None:
            print("delete experiment.")
            experiment_url = f"{self.pre_check.mlplatform_addr}/experiments"
            delete_experiment_data = [self.experiment_id]
            res = requests.delete(
                experiment_url, json=delete_experiment_data, headers=self.pre_check.mlplatform_request_header
            )
            if res.status_code != 200:
                print(f"delete experiment failed. reason:{res.text}")

    def run(self):
        try:
            self._experiment()
            self._train()
            """
            self._retrain()
            self._inference()
            self._inference_download()
            self._serving()
            """
            if self.experiment_id is not None:
                self._delete_experiment()
        except Exception as e:
            if self.experiment_id is not None:
                self._delete_experiment()
            raise e
