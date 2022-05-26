from odoo import _, models, fields, api
from odoo.addons.queue_job.job import job


# TODO: If this modifications are useful for other projects, we can move them
# to a separate module.
class L10nEsAeatReport(models.AbstractModel):
    _inherit = "l10n.es.aeat.report"

    state = fields.Selection(
        selection_add=[
            ('calculating', 'Calculating in background'),
        ]
    )

    @api.multi
    def button_calculate_background(self):
        uid = self.env.context.get('uid', 1)
        for report in self:
            report.with_delay()._bg_calculate(uid)
        self.write({"state": "calculating"})

    @job
    def _bg_calculate(self, uid):
        try:
            self.button_calculate()
            self.create_activity(uid)
            self.write({"state": "calculated"})
        except Exception as ex:
            self.env.cr.rollback()
            self.write({"state": "draft"})
            self.message_post(
                _("Error calculating the model. More details in the queue job. Please contact with IT team.")  # noqa
            )
            self.env.cr.commit()
            raise ex

    def create_activity(self, uid):
        self.env['mail.activity'].create({
            'res_id': self.id,
            'res_model_id': self.env['ir.model'].search(
                [('model', '=', 'l10n.es.aeat.mod347.report')]
            ).id,
            'summary': _("Modelo 347 calculated. Ready to review."),
            'user_id': uid,
            'activity_type_id': self.env.ref("mail.mail_activity_data_todo").id,
        })
