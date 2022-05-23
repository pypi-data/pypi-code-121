from pathlib import Path
from typing import List, Dict
import json
from google.api_core import retry
from google.cloud import bigquery_reservation_v1
from google.protobuf import field_mask_pb2
import bqslots.lock as lock


def box_print(msg, indent=1, width=None, title=None):
    """
    Need I say more?
    :param msg:
    :param indent:
    :param width:
    :param title:
    :return:
    """
    lines = msg.split("\n")
    space = " " * indent
    if not width:
        width = max(map(len, lines))
    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f"║{space}{title:<{width}}{space}║\n"  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += "".join([f"║{space}{line:<{width}}{space}║\n" for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    print(box)


class Client:
    """
    wrapper for reservation client, each client is for one project and reservation
    type

    example:


    """

    MAX_SLOTS_MESSAGE = "SLOTS_QUOTA_REACHED"
    standard_retry = retry.Retry(deadline=120, predicate=Exception)

    def __init__(
            self,
            admin_project: str,
            admin_region: str,
            reservation: str,
            max_slots_quota: int,
            user_project: str,
            gcs_lock_bucket=None
    ):
        self.admin_project = admin_project
        self.admin_region = admin_region
        self.reservation = (
            reservation.lower()
        )  # i.e "default" needs to be lowercase api calls
        self.max_slots_quota = max_slots_quota
        self.user_project = user_project
        self.admin_project_region_path = (
            f"projects/{admin_project}/locations/{admin_region}"
        )
        self.reservation_path = (
            f"{self.admin_project_region_path}/reservations/{reservation}"
        )
        self.reservation_api = bigquery_reservation_v1.ReservationServiceClient()
        self.last_slot_commit = None

        self.using_lock = False
        if gcs_lock_bucket:
            self.lock_client = lock.Client(bucket=gcs_lock_bucket, lock_file_path="slots-lock.txt", ttl=30)
            self.using_lock = True

    def allocate_slots(self, slots: int) -> str:
        """
        allocate slots
        :param slots:
        :return: commitment_id str
        """

        commit = self._purchase_commitment(slots)
        return commit

    def increment_reservation(self, slots: int):
        """
        :param slots:
        :return:
        """
        # do stuff
        if self.using_lock:
            self.lock_client.wait_for_lock_expo()

        self._increment_slots_number_on_reservation(slots)
        if not self._reservation_assigned_to_project():
            self._create_assignment()

        if self.using_lock:
            self.lock_client.free_lock()

    def clear_slots_commitment(self, commitment_id: str):
        """
        :param commitment_id:
        :return:
        """

        if commitment_id == self.MAX_SLOTS_MESSAGE:
            print(self.MAX_SLOTS_MESSAGE)
            return

        # do stuff
        if self.using_lock:
            self.lock_client.wait_for_lock_expo()

        commit = self.reservation_api.get_capacity_commitment(
            name=commitment_id,
            retry=self.standard_retry,
        )
        commit_slots = commit.slot_count
        self._decrement_slots_number_on_reservation(commit_slots)

        reservation_amount = self._get_number_of_slots_allocated_reservation()
        total_slots_used = self._get_total_number_of_slots_allocated_admin_project()

        if reservation_amount == 0:
            self._clear_assignments_for_reservation()

        self._clear_slots(commitment_id)

        if self.using_lock:
            self.lock_client.free_lock()

        msg = f"""
                commitment: {commitment_id} -> DELETED
                reservation_amount left: {reservation_amount}
                total_slots_used on admin project: {total_slots_used}
              """
        box_print(msg=msg, indent=20)

    @staticmethod
    def write_dict_to_json_file(path: str, filename: str, data: Dict):
        """
        :param path:
        :param filename:
        :param data:
        :return:
        """
        p = Path(path)
        p.mkdir(exist_ok=True, parents=True)
        (p / filename).open("w").write(json.dumps(data))

    def _decrement_slots_number_on_reservation(self, slots: int):
        """

        :param slots:
        :return:
        """
        slots_num = -abs(slots)
        self._change_reservation_slots_amount(slots_num)

    def _increment_slots_number_on_reservation(self, slots: int):
        """

        :param slots:
        :return:
        """

        self._change_reservation_slots_amount(abs(slots))

    def _purchase_commitment(self, slots) -> str:
        """
        Create a commitment for a specific amount of slots (in increments of 500).
        :param slots: Number of slots to purchase
        :return: the commit name
        """

        if (
                slots + self._get_total_number_of_slots_allocated_admin_project()
                > self.max_slots_quota
        ):
            return self.MAX_SLOTS_MESSAGE

        commit_config = bigquery_reservation_v1.CapacityCommitment(
            plan="FLEX", slot_count=slots,
        )

        commit = self.reservation_api.create_capacity_commitment(
            parent=self.admin_project_region_path, capacity_commitment=commit_config, retry=self.standard_retry
        )
        self.last_slot_commit = commit.name
        box_print(f"purchased commit:{commit.name}")

        return commit.name

    def _get_total_number_of_slots_allocated_admin_project(self) -> int:
        """

        :return:
        """
        list_slot_counts = [
            i.slot_count
            for i in self.reservation_api.list_capacity_commitments(
                parent=self.admin_project_region_path, retry=self.standard_retry
            )
        ]

        return sum(list_slot_counts)

    def _get_number_of_slots_allocated_reservation(self):
        """

        :return:
        """
        res = self.reservation_api.get_reservation(
            name=self.reservation_path,
            retry=self.standard_retry,
        )
        return res.slot_capacity

    def _create_assignment(self):
        """
        Create an assignment of either an organization, folders or projects to a specific reservation.
        :param reservation_id: The reservation id from which the project id will be assigned
        :param user_project: The project id that will use be assigned to this reservation
        :return: the assignment name
        """
        assign_config = bigquery_reservation_v1.Assignment(
            job_type="QUERY", assignee=f"projects/{self.user_project}"
        )

        try:
            assign = self.reservation_api.create_assignment(
                parent=self.reservation_path,
                assignment=assign_config,
                retry=self.standard_retry,
            )
            return assign.name

        except Exception as e:
            print(e)

    def _change_reservation_slots_amount(self, amount=100):
        """
        :param amount:
        :return:
        """

        res = self.reservation_api.get_reservation(name=self.reservation_path, retry=retry.Retry(deadline=90, predicate=Exception, maximum=2))
        desired_slots_amount = res.slot_capacity + amount

        if desired_slots_amount <= 0:  # can not set to negative
            desired_slots_amount = 0

        res.slot_capacity = desired_slots_amount
        update_mask = field_mask_pb2.FieldMask(paths=["slot_capacity"])
        final_res = self.reservation_api.update_reservation(
            reservation=res,
            update_mask=update_mask,
            retry=self.standard_retry,
        )

        assert final_res.slot_capacity == desired_slots_amount, "slots not allocated"

    def _reservation_assigned_to_project(self):
        """
        :return:
        """
        for assignment in self._list_assignments():
            if self.reservation_path in assignment:
                return True

        return False

    def _list_assignments(self) -> List:
        """

        :return:
        """
        list_reservations = [
            i.name
            for i in self.reservation_api.list_reservations(
                parent=self.admin_project_region_path, retry=self.standard_retry
            )
        ]
        assignments = []
        for i in list(map(lambda x: x.split("/")[-1], list_reservations)):
            assignments.extend(
                [
                    i.name
                    for i in self.reservation_api.list_assignments(
                    parent=self.admin_project_region_path + "/reservations/" + i
                )
                ]
            )
        return assignments

    def _clear_assignments_for_reservation(self):
        """

        :return:
        """
        # ``projects/myproject/locations/US/reservations/team1-prod/assignments/123``
        assignment = self._get_assignment_for_reservation()
        self.reservation_api.delete_assignment(
            name=assignment,
            retry=self.standard_retry,
        )

    def _get_assignment_for_reservation(self):
        """

        :return:
        """
        # there should only be one assignment per reservation
        list_assignments = self.reservation_api.list_assignments(
            parent=self.reservation_path, retry=self.standard_retry
        )

        # we get a list of assigment ids like
        # ``projects/myproject/locations/US/reservations/team1-prod/assignments/123``
        assignment = [assignment.name for assignment in list_assignments][0]
        return assignment

    def _clear_slots(self, commit_id: str):
        """

        :param commit_id:
        :return:
        """
        self.reservation_api.delete_capacity_commitment(
            name=commit_id,
            retry=self.standard_retry
        )
