# -*- coding: utf-8 -*-
from odoo.http import request
from odoo.addons.easy_my_coop_website.controllers.main import WebsiteSubscription
from odoo import http
from odoo.http import request
from datetime import datetime


class WebsiteSubscription(WebsiteSubscription):

    def fill_values(self, values, is_company, logged, load_from_user=False):
        values = super(WebsiteSubscription, self).fill_values(values, is_company, logged, load_from_user=False)
        sub_req_obj = request.env['subscription.request']
        fields_desc = sub_req_obj.sudo().fields_get(['join_commission', 'discovery_channel'])
        values.update({
            'commissions': fields_desc['join_commission']['selection'],
            'channels': fields_desc['discovery_channel']['selection'],
        })
        return values

    @http.route(
        ["/subscription/subscribe_share"],
        type="http",
        auth="public",
        website=True,
    )

    def share_subscription(self, **kwargs):
        sub_req_obj = request.env["subscription.request"]
        attach_obj = request.env["ir.attachment"]

        # List of file to add to ir_attachment once we have the ID
        post_file = []
        # Info to add after the message
        post_description = []
        values = {}

        for field_name, field_value in kwargs.items():
            if type(field_value) == "filename":
                post_file.append(field_value)
            elif (
                field_name in sub_req_obj._fields
            ):
                values[field_name] = field_value

        response = self.validation(kwargs, None, values, post_file)
        if response is not True:
            return response

        lastname = kwargs.get("lastname").upper()
        firstname = kwargs.get("firstname").title()

        values["name"] = firstname + " " + lastname
        values["lastname"] = lastname
        values["firstname"] = firstname
        values["birthdate"] = datetime.strptime(
            kwargs.get("birthdate"), "%d/%m/%Y"
        ).date()
        values["source"] = "website"

        values["share_product_id"] = self.get_selected_share(kwargs).id

        subscription_id = sub_req_obj.sudo().create(values)

        if subscription_id:
            for field_value in post_file:
                attachment_value = {
                    "name": field_value.filename,
                    "res_name": field_value.filename,
                    "res_model": "subscription.request",
                    "res_id": subscription_id,
                    "datas": base64.encodestring(field_value.read()),
                    "datas_fname": field_value.filename,
                }
                attach_obj.sudo().create(attachment_value)

        return self.get_subscription_response(values, kwargs)
