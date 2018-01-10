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
import dateutil.parser
from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.model
    def get_standard_price(self):
        bom_price = 0.0
        for bom_line in self.bom_line_ids:
            line_price = bom_line.product_id.standard_price * bom_line.product_qty
            bom_price += line_price
        for byproduct_bom_line in self.sub_products:
            line_price = byproduct_bom_line.product_id.standard_price * byproduct_bom_line.product_qty
            bom_price -= line_price
        return bom_price

    @api.one
    def write(self, vals):
        res = super(MrpBom, self).write(vals)
        self.write_cost_price()
        return res
    
    @api.model
    def create(self, vals):
        res = super(MrpBom, self).create(vals)
        self.write_cost_price()
        return res
        
    @api.model
    def write_cost_price(self):
        _logger.debug(self.get_standard_price())
        if self.is_bom_valid_on(datetime.datetime.now().date()) and self.product_id:
            standard_bom_price = self.get_standard_price()
            self.product_id.write({'standard_price': standard_bom_price})

    @api.model
    def is_bom_valid_on(self, date):
        date_start = False
        date_stop = False
        if self.date_start:
            date_start = dateutil.parser.parse(self.date_start).date()
        if self.date_stop:
            date_stop = dateutil.parser.parse(self.date_stop).date() or False
        if date_start and not date_stop:
            if date >= date_start:
                return True
        if date_start and date_stop:
            if date <= date_start <= date_stop:
                return True
        if not date_start and date_stop:
            if date <= date_stop:
                return True
        if not date_start and not date_stop:
            return True
        return False
