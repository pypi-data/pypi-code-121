from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    imd_tmpl = env['ir.model.data'].search([
        ('name', '=', 'DadesAddicionals1GBSenseCost_product_template')
    ])
    imd_tmpl_500 = env['ir.model.data'].search([
        ('name', '=', 'DadesAddicionals500MB_product_template')
    ])
    if not imd_tmpl or imd_tmpl.res_id == imd_tmpl_500.res_id:
        one_gb_wo_cost_template = env['product.template'].create({
            'name': "1GB addicional sense cost per l'usuari",
            'categ_id': env.ref('somconnexio.mobile_oneshot_service').id,
        })
        # When a new template is created, it also creates one new product.product
        default_variant = one_gb_wo_cost_template.product_variant_ids
        if not imd_tmpl:
            env['ir.model.data'].create({
                'model': 'product.template',
                'module': 'somconnexio',
                'name': 'DadesAddicionals1GBSenseCost_product_template',
                'res_id': one_gb_wo_cost_template.id,
            })
        else:
            imd_tmpl.res_id = one_gb_wo_cost_template.id
        products = tuple(
            elem.id
            for elem in [
                env.ref('somconnexio.DadesAddicionals1GBSenseCost', False),
                env.ref('somconnexio.DadesAddicionals3GBSenseCost', False),
                env.ref('somconnexio.DadesAddicionals5GBSenseCost', False),
                env.ref('somconnexio.DadesAddicionals10GBSenseCost', False)
            ]
            if elem
        )
        cr.execute(
            'UPDATE product_product SET product_tmpl_id = %s WHERE id in %s',
            (imd_tmpl.res_id, products)
        )
        default_variant.unlink()
