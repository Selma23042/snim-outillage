from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FicheVieMateriel(models.Model):
    _name        = 'snim.fiche.vie.materiel'
    _description = 'Fiche de vie materiel SNIM'
    _order       = 'date_etalonnage desc'

    name = fields.Char(
        string='Reference',
        compute='_compute_name',
        store=True)
    num_procedure = fields.Char(
        string='Numero procedure', required=True)
    lieu_affectation = fields.Char(
        string='Lieu affectation', required=True)
    date_etalonnage = fields.Date(
        string='Date etalonnage', required=True)
    date_proch_etalonnage = fields.Date(
        string='Date prochaine', required=True)
    nature = fields.Selection([
        ('interne', 'Interne'),
        ('externe', 'Externe'),
    ], string='Nature', required=True)
    resultats = fields.Text(
        string='Resultats')
    decision = fields.Selection([
        ('conforme',     'Conforme'),
        ('non_conforme', 'Non conforme'),
        ('ajourne',      'Ajourne'),
    ], string='Decision', required=True)
    entite = fields.Char(
        string='Entite', required=True)
    visa_resp = fields.Char(
        string='Visa responsable', required=True)
    instrument_id = fields.Many2one(
        'snim.instrument',
        string='Instrument',
        required=True,
        ondelete='cascade')

    @api.depends('instrument_id', 'date_etalonnage')
    def _compute_name(self):
        for rec in self:
            if rec.instrument_id and rec.date_etalonnage:
                rec.name = (
                    f"FV-{rec.instrument_id.code}"
                    f"-{rec.date_etalonnage}"
                )
            else:
                rec.name = 'Nouvelle fiche'

    @api.constrains('date_etalonnage', 'date_proch_etalonnage')
    def _check_dates(self):
        for rec in self:
            if (rec.date_etalonnage
                    and rec.date_proch_etalonnage
                    and rec.date_proch_etalonnage
                    <= rec.date_etalonnage):
                raise ValidationError(
                    'La date prochaine doit etre '
                    'superieure a la date etalonnage.')
