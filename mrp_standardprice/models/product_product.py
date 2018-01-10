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

import datetime

from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.one
    def save_bom_costprice(self):
        bom_lines = self.env['mrp.bom.line'].search([('product_id', '=', self.id)])
        for bom_line in bom_lines:
            parent_bom = bom_line.bom_id
            if parent_bom.is_bom_valid_on(datetime.datetime.now().date()) and parent_bom.product_id:
                standard_bom_price = parent_bom.get_standard_price()
                parent_bom.product_id.write({'standard_price': standard_bom_price})
