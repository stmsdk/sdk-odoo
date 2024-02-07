# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class q2_stock_picking(models.Model):
#     _name = 'q2_stock_picking.q2_stock_picking'
#     _description = 'q2_stock_picking.q2_stock_picking'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


"""
........................update stock_quant set quantity=0 where location_id in (8,9,10,11,12) and create_date < '2023-12-31 23:59:59.99999';

select * from product_template where id in (select product_tmpl_id from product_product where (default_code = '') IS NOT FALSE) and type ='consu' and name like 'ST%'

update stock_quant set quantity=0 where reserved_quantity>0 and create_date < '2023-12-31 23:59:59.99999';
update stock_quant set quantity=0 where reserved_quantity<0 and create_date < '2023-12-31 23:59:59.99999';
update stock_picking set invoice_state='none' , note='autocierre_2023' where invoice_state='2binvoiced' and create_date < '2023-12-31 23:59:59.99999';
update stock_picking set state='done' , note='autocierre_2023' where state in ('assigned','waiting', 'Waiting Another Operation','confirmed') and create_date < '2023-12-31 23:59:59.99999';
update stock_picking set invoice_state='none' , note='autocierre_2023' where invoice_state='2binvoiced' and create_date < '2023-12-31 23:59:59.99999';
update mrp_production set state='done' , client_order_ref = 'autocierre_2023' where state in ('draft','confirmed','progress','to_close') and create_date < '2023-12-31 23:59:59.99999';

/*
select * from stock_quant as q where location_id = 9 and quantity<0;
select * from product_product where id = 8546;
select * from stock_quant where product_id = 8546;
select * from product_product where id = 38550;
select * from stock_quant where product_id = 38550;
select * from stock_quant where product_id = 18021;
select * from product_product where id = 18021;
select * from product_product where id = 42394;
select * from stock_quant where product_id = 42394
select * from stock_quant as q where location_id = 11
select * from stock_quant as q where location_id = 9
select * from product_product where default_code = 'RPLAPEVKU5001'
select * from stock_quant where location_id = 4
select * from stock_quant where product_id = 28167
select * from stock_quant where product_id = (	select id from product_product where default_code='FRI01023100')
select id from product_product where default_code='FRI01023100'
select * from stock_quant where product_id = 1004
select * from product_product where id=38550
select * from stock_quant where reserved_quantity>0
select * from stock_picking
where invoice_state not in ('2binvoiced','none','invoiced')
*/
"""