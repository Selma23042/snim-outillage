from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class Instrument(models.Model):
    _name        = 'snim.instrument'
    _description = 'Instrument de mesure SNIM'
    _inherit     = ['mail.thread', 'mail.activity.mixin']
    _order       = 'code asc'

    code = fields.Char(
        string='Code', required=True,
        tracking=True)
    designation = fields.Char(
        string='Designation', required=True,
        tracking=True)
    capacite = fields.Char(
        string='Capacite', required=True)
    detenu_par = fields.Char(
        string='Detenu par', required=True)
    affectation = fields.Char(
        string='Affectation a', required=True)
    periodicite = fields.Integer(
        string='Periodicite (mois)',
        required=True, default=12)
    marque = fields.Char(
        string='Marque')
    date_mise_en_service = fields.Date(
        string='Date mise en service',
        required=True)
    date_der_etalonnage = fields.Date(
        string='Derniere etalonnage',
        required=True, tracking=True)
    date_pro_etalonnage = fields.Date(
        string='Prochaine etalonnage',
        compute='_compute_date_pro',
        store=True)
    motif = fields.Text(
        string='Motif')
    statut = fields.Selection([
        ('en_attente',   'En attente'),
        ('conforme',     'Conforme'),
        ('non_conforme', 'Non conforme'),
        ('reforme',      'Reforme'),
    ], string='Statut', default='en_attente',
       tracking=True)

    fiche_vie_ids = fields.One2many(
        'snim.fiche.vie.materiel',
        'instrument_id',
        string='Fiches de vie')
    fiche_vie_count = fields.Integer(
        compute='_compute_fiche_count',
        string='Nb fiches')

    reforme_ids = fields.One2many(
        'snim.reforme',
        'instrument_id',
        string='Reformes')

    @api.depends('date_der_etalonnage', 'periodicite')
    def _compute_date_pro(self):
        for rec in self:
            if rec.date_der_etalonnage and rec.periodicite:
                rec.date_pro_etalonnage = (
                    rec.date_der_etalonnage
                    + relativedelta(months=rec.periodicite)
                )
            else:
                rec.date_pro_etalonnage = False

    def _compute_fiche_count(self):
        for rec in self:
            rec.fiche_vie_count = len(rec.fiche_vie_ids)

    def action_voir_fiches(self):
        return {
            'type'     : 'ir.actions.act_window',
            'name'     : 'Fiches de vie',
            'res_model': 'snim.fiche.vie.materiel',
            'view_mode': 'list,form',
            'domain'   : [('instrument_id', '=', self.id)],
            'context'  : {'default_instrument_id': self.id},
        }

    @api.constrains('periodicite')
    def _check_periodicite(self):
        for rec in self:
            if rec.periodicite <= 0:
                raise ValidationError(
                    'La periodicite doit etre > 0.')

    def action_delete(self):
        name = self.code
        self.unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Suppression',
                'message': f'Instrument {name} supprime.',
                'type': 'warning',
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def action_edit(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'snim.instrument',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }