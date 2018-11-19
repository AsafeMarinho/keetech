# -*- coding: utf-8 -*-

from odoo import http, _

class RadarNFe(http.Controller):
    @http.route('/e-radar/', type="http", auth="user", website=True)
    def index(self, sortby=None):

        searchbar_sortings = {
            'date': {'label': _('Data'), 'd': 'data_evento desc'},
            'name': {'label': _('Emitente'), 'd': 'partner_id'},
            #'stage': {'label': _('Stage'), 'd': 'nfe_state'},
        }

        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['d']

        list_dfe = http.request.env['sped.dfe.query.nsu'].sudo().search([], order=sort_order)
        #values = list_dfe.browse()

        return http.request.render("br_dfe.radar",
                                   {"dfe": list_dfe,
                                    'searchbar_sortings': searchbar_sortings,
                                    'sortby': sortby})