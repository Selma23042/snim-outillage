from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class Reforme(models.Model):
    _name        = 'snim.reforme'
    _description = 'Reforme instrument SNIM'
    _order       = 'date_reforme desc'

    name = fields.Char(
        string='Reference',
        compute='_compute_name',
        store=True)
    date_reforme = fields.Date(
        string='Date reforme',
        required=True,
        default=fields.Date.today)
    motif = fields.Text(
        string='Motif', required=True)
    instrument_id = fields.Many2one(
        'snim.instrument',
        string='Instrument',
        required=True,
        ondelete='cascade')

    @api.depends('instrument_id', 'date_reforme')
    def _compute_name(self):
        for rec in self:
            if rec.instrument_id and rec.date_reforme:
                rec.name = (
                    f"REF-{rec.instrument_id.code}"
                    f"-{rec.date_reforme}"
                )
            else:
                rec.name = 'Nouvelle reforme'

    @api.constrains('date_reforme')
    def _check_date(self):
        for rec in self:
            if rec.date_reforme > date.today():
                raise ValidationError(
                    'La date ne peut pas '
                    'etre dans le futur.')
