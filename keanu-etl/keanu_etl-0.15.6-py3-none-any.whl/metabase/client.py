import logging

from metabase import Metabase

from .helpers import *

metabase_io_log = logging.getLogger("metabase.io")


class Client:
    """
    Wrapper around Metabase client for not having to deal with response status
    and to provide shorcut methods
    """

    def __init__(self):
        self.client = Metabase()

    def get(self, model, model_id=None, subquery=None):
        """
        Generic get method to retrieve a specific object or sub-objects
        """
        if subquery is not None:
            query = "/{}/{}/{}".format(model, model_id, subquery)
        elif model_id is not None:
            query = "/{}/{}".format(model, model_id)
        else:
            query = "/{}/".format(model)

        status, item = self.client.get(query)
        if not status:
            if subquery is not None:
                msg = "Error while retrieving {} for {} {}".format(
                    subquery, model, model_id
                )
            elif model_id is not None:
                msg = "Error while retrieving {} {}".format(model, model_id)
            else:
                msg = "Error while retrieving {} list".format(model)
            raise Exception(msg)

        return item

    def get_by_name(self, model, name):
        """
        Retrieve an object by name.
        Search done on the client side, so watch out if there are many objects of that model
        """
        status, models = self.client.get("/{}/".format(model))
        if not status:
            raise Exception("Error while retrieving {}s".format(model))

        models = list(filter(lambda m: m["name"] == name, models))
        if len(models) == 0:
            raise Exception("No such {}: {}".format(model, name))

        return models[0]

    def add_card(self, card, collection_id):
        card["collection_id"] = api_collection_id(collection_id)
        status, result = self.client.post("/card/", json=card)
        if not status:
            raise Exception("Could not create card {}".format(card["name"]))
        return result

    def update_card(self, card, collection_id):
        # import ipdb; ipdb.set_trace()
        card["collection_id"] = api_collection_id(collection_id)
        status = self.client.put("/card/{}".format(card["id"]), json=card)
        if not status:
            raise Exception(
                "Could not update card {} (id {})".format(card["name"], card["id"])
            )
        return card

    def add_dashboard(self, dashboard, collection_id):
        dashboard["collection_id"] = api_collection_id(collection_id)
        status, result = self.client.post("/dashboard/", json=dashboard)
        if not status:
            raise Exception("Could not create dashboard {}".format(dashboard["name"]))
        return result

    def update_dashboard(self, dashboard, collection_id):
        dashboard["collection_id"] = api_collection_id(collection_id)
        status = self.client.put(
            "/dashboard/{}".format(dashboard["id"]), json=dashboard
        )
        if not status:
            raise Exception(
                "Could not update dashboard {} (id {})".format(
                    dashboard["name"], dashboard["id"]
                )
            )
        return dashboard

    def add_dashboard_card(self, card, dashboard_id):
        status, result = self.client.post(
            "/dashboard/{}/cards".format(dashboard_id), json=card
        )
        if not status:
            raise Exception(
                "Could not add card {} to dashboard {}".format(
                    card.get("cardId", "(no cardId)"), dashboard_id
                )
            )
        return result

    def clear_dashboard(self, dashboard):
        status, existing = self.client.get("/dashboard/{}".format(dashboard["id"]))
        for card in existing["ordered_cards"]:
            status = self.client.delete(
                "/dashboard/{}/cards".format(dashboard["id"]),
                params={"dashcardId": card["id"]},
            )

            if not status:
                raise Exception(
                    "Could not clear dashboard {} (id {})".format(
                        dashboard["name"], dashboard["id"]
                    )
                )

    def add_collection(self, collection, parent_id):
        params = {k: collection[k] for k in ["name", "description", "color"]}
        # The root coolection has a special non-integer id, but the API accepts only integer values...
        # The special value None means root collection.
        params["parent_id"] = api_collection_id(parent_id)
        status, result = self.client.post("/collection/", json=params)
        if not status:
            raise Exception("Could not create collection {}".format(params["name"]))
        return result

    def update_collection(self, collection, parent_id):
        params = {k: collection[k] for k in ["name", "description", "color"]}
        params["parent_id"] = api_collection_id(parent_id)
        status = self.client.put("/collection/{}".format(collection["id"]), json=params)
        if not status:
            raise Exception(
                "Could not update collection {} (id {})".format(
                    params["name"], collection["id"]
                )
            )
        return collection

    def add_dimension(self, dimension, field_id):
        status, result = self.client.post(
            "/field/{}/dimension".format(field_id), json=dimension
        )
        if not status:
            raise Exception("Could not add dimension to field {}".format(field_id))
        return result

    def add_segment(self, segment):
        status, result = self.client.post("/segment/", json=segment)
        if not status:
            raise Exception("Could not create segment {}".format(segment["name"]))
        return result

    def update_segment(self, segment):
        status = self.client.put("/segment/{}".format(segment["id"]), json=segment)
        if not status:
            raise Exception(
                "Could not update segment {} (id {})".format(
                    segment["name"], segment["id"]
                )
            )
        return segment

    def update_field(self, field_id, params):
        status = self.client.put("/field/{}".format(field_id), json=params)
        if not status:
            raise Exception("Could not update field {}".format(field_id))
