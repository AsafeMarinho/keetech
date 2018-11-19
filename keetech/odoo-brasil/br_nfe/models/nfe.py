# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

# Métodos de Pagamento conforme modelo para emissão de NF-e
metodos = [
    ('01', u'01 - Dinheiro'),
    ('02', u'02 - Cheque'),
    ('03', u'03 - Cartão de Crédito'),
    ('04', u'04 - Cartão de Débito'),
    ('05', u'05 - Crédito Loja'),
    ('10', u'10 - Vale Alimentacão'),
    ('11', u'11 - Vale Refeição'),
    ('12', u'12 - Vale Presente'),
    ('13', u'13 - Vale Combustível'),
    ('15', u'15 - Boleto Bancário'),
    ('90', u'90 - Sem Pagamento'),
    ('99', u'99 - Outros'), ]


class ImportDeclaration(models.Model):
    _inherit = 'br_account.import.declaration'

    invoice_eletronic_line_id = fields.Many2one(
        'invoice.eletronic.item', u'Linha de Documento Eletrônico',
        ondelete='cascade', index=True)


class AccountDocumentRelated(models.Model):
    _inherit = 'br_account.document.related'

    invoice_eletronic_id = fields.Many2one(
        'invoice.eletronic', u'Documento Eletrônico', ondelete='cascade')

    @api.onchange('invoice_related_id')
    def onchange_br_nfe_invoice_related_id(self):
        if len(self.invoice_related_id.invoice_eletronic_ids) > 0:
            self.access_key = \
                self.invoice_related_id.invoice_eletronic_ids[0].chave_nfe


class NfeReboque(models.Model):
    _name = 'nfe.reboque'

    invoice_eletronic_id = fields.Many2one('invoice.eletronic', string="NFe")
    placa_veiculo = fields.Char(string="Placa", size=7)
    uf_veiculo = fields.Char(string=u"UF Veículo", size=2)
    rntc = fields.Char(string="RNTC", size=20,
                       help="Registro Nacional de Transportador de Carga")
    vagao = fields.Char(string=u"Vagão", size=20)
    balsa = fields.Char(string="Balsa", size=20)


class NfeVolume(models.Model):
    _name = 'nfe.volume'

    invoice_eletronic_id = fields.Many2one('invoice.eletronic', string="NFe")
    quantidade_volumes = fields.Integer(string="Qtde. Volumes")
    especie = fields.Char(string=u"Espécie", size=60)
    marca = fields.Char(string="Marca", size=60)
    numeracao = fields.Char(string=u"Numeração", size=60)
    peso_liquido = fields.Float(string=u"Peso Líquido")
    peso_bruto = fields.Float(string="Peso Bruto")


class NFeCobrancaDuplicata(models.Model):
    _name = 'nfe.duplicata'
    _order = 'data_vencimento'

    invoice_eletronic_id = fields.Many2one('invoice.eletronic', string="NFe")
    currency_id = fields.Many2one(
        'res.currency', related='invoice_eletronic_id.currency_id',
        string="EDoc Currency", readonly=True)
    numero_duplicata = fields.Char(string=u"Número Duplicata", size=60)
    data_vencimento = fields.Date(string="Data Vencimento")
    valor = fields.Monetary(string="Valor Duplicata")

class NFePagamentos(models.Model):
    _name = 'nfe.pagamentos'

    invoice_eletronic_id = fields.Many2one('invoice.eletronic', string="NFe")
    currency_id = fields.Many2one(
        'res.currency', related='invoice_eletronic_id.currency_id',
        string="EDoc Currency", readonly=True)
    metodo_pagamento = fields.Selection(metodos, string=u'Método de Pagamento')
    valor = fields.Monetary(string=u'Método de Pagamento')
