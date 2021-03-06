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

from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    @api.one
    def write(self, vals):
        super(ProductTemplate, self).write(vals)
        for product_product in self.product_variant_ids:
            bom_lines = self.env['mrp.bom.line'].search([('product_id','=',product_product.id)])
            for bom_line in bom_lines:
                parent_bom = bom_line.bom_id
                bom_price = 0
                for parent_bom_line in parent_bom.bom_line_ids:
                    line_price = parent_bom_line.product_id.standard_price *  parent_bom_line.product_qty
                    bom_price += line_price
                parent_bom.product_id.write({'standard_price': bom_price})
        return super(ProductTemplate, self).write(vals)