from odoo import api, fields, models


class BeesdooProduct(models.Model):

    _inherit = "product.template"

    @api.multi
    @api.depends(
        "taxes_id",
        "standard_price",
        "taxes_id.amount",
        "taxes_id.tax_group_id",
        "display_weight",
        "weight",
    )
    def _compute_total(self):
        for product in self:
            price = (
                product.with_context(pricelist=1).price
                if product.id else 0
            )
            consignes_group = self.env.ref(
                "beesdoo_product.consignes_group_tax", raise_if_not_found=False
            )

            taxes_included = set(product.taxes_id.mapped("price_include"))
            if len(taxes_included) == 0:
                product.total_with_vat = price
                return True

            elif len(taxes_included) > 1:
                raise ValidationError(
                    _("Several tax strategies (price_include) defined for %s")
                    % product.name
                )

            elif taxes_included.pop():
                product.total_with_vat = price
                product.total_deposit = sum(
                    [
                        tax._compute_amount(
                            price, price
                        )
                        for tax in product.taxes_id
                        if tax.tax_group_id == consignes_group
                    ]
                )
            else:
                tax_amount_sum = sum(
                    [
                        tax._compute_amount(
                            price, price
                        )
                        for tax in product.taxes_id
                        if tax.tax_group_id != consignes_group
                    ]
                )
                product.total_with_vat = price + tax_amount_sum

            product.total_deposit = sum(
                [
                    tax._compute_amount(price, price)
                    for tax in product.taxes_id
                    if tax.tax_group_id == consignes_group
                ]
            )

            if product.display_weight > 0:
                product.total_with_vat_by_unit = (
                    product.total_with_vat / product.weight
                )

