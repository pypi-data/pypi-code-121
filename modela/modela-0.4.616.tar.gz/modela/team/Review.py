import grpc
from github.com.metaprov.modelaapi.pkg.apis.team.v1alpha1.generated_pb2 import Review as MDReview
from github.com.metaprov.modelaapi.services.review.v1.review_pb2_grpc import ReviewServiceStub
from github.com.metaprov.modelaapi.services.review.v1.review_pb2 import CreateReviewRequest, \
    UpdateReviewRequest, \
    DeleteReviewRequest, GetReviewRequest, ListReviewRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Review(Resource):
    def __init__(self, item: MDReview = MDReview(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class ReviewClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: ReviewServiceStub = stub

    def create(self, review: Review) -> bool:
        request = CreateReviewRequest()
        request.review.CopyFrom(review.raw_message)
        try:
            response = self.__stub.CreateReview(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, review: Review) -> bool:
        request = UpdateReviewRequest()
        request.review.CopyFrom(review.raw_message)
        try:
            self.__stub.UpdateReview(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Review, bool]:
        request = GetReviewRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetReview(request)
            return Review(response.review, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteReviewRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteReview(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Review], bool]:
        request = ListReviewRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListReviews(request)
            return [Review(item, self) for item in response.reviews.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


