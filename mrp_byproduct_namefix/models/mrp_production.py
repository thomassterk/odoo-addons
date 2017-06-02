# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2017 Thomas Sterk (www.thomas-sterk.nl).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
import time
import openerp.addons.decimal_precision as dp
from openerp import models, fields, api, _
from collections import OrderedDict
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import float_compare, float_is_zero
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID
from openerp.addons.product import _common

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms production order and calculates quantity based on subproduct_type.
        @return: Newly generated picking Id.
        """
        move_obj = self.pool.get('stock.move')
        picking_id = super(mrp_production,self).action_confirm(cr, uid, ids, context=context)
        product_uom_obj = self.pool.get('product.uom')
        for production in self.browse(cr, uid, ids):
            source = production.product_id.property_stock_production.id
            if not production.bom_id:
                continue
            for sub_product in production.bom_id.sub_products:
                product_uom_factor = product_uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, production.bom_id.product_uom.id)
                qty1 = sub_product.product_qty
                if sub_product.subproduct_type == 'variable':
                    if production.product_qty:
                        qty1 *= product_uom_factor / (production.bom_id.product_qty or 1.0)
                data = {
                    'name': production.name,
                    'date': production.date_planned,
                    'product_id': sub_product.product_id.id,
                    'product_uom_qty': qty1,
                    'product_uom': sub_product.product_uom.id,
                    'location_id': source,
                    'location_dest_id': production.location_dest_id.id,
                    'production_id': production.id,
                    'origin': production.name,
                }
                move_id = move_obj.create(cr, uid, data, context=context)
                move_obj.action_confirm(cr, uid, [move_id], context=context)

        return picking_id
        