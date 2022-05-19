CREATE OR REPLACE PROCEDURE public.close_period(IN sdb sys_dashboard, IN cal_now calendar)
 LANGUAGE hyperc
AS $procedure$
assert sdb.splited_proc == '-'
#Sell_proc
assert sdb.CURRENT_SOLD_ITEM == sdb.ITEMS_COUNT + 1 #overcounting_of_sku_qty
sdb.CURRENT_SOLD_ITEM = 1	#reset_count_if_products
assert cal_now.WEEK_START_DATE == sdb.CURRENT_CALCULATED_DATE
sdb.CURRENT_CALCULATED_DATE = cal_now.NEXT_WEEK_START_DATE
sdb.CURRENT_CALCULATED_WEEK += 1
sdb.order_index = 1
$procedure$
;

CREATE OR REPLACE PROCEDURE public.init_globals(IN sdb sys_dashboard, IN lc logistic_costs)
 LANGUAGE hyperc
AS $procedure$
assert sdb.splited_proc == '-'
assert sdb.initiated == 'no'
global prods_str # type: products
global cal_now_str # type: calendar
global report_str # type: report
global bxt_str # type: box_templates
global lc_str # type: logistic_costs
global in_deliv_str # type: in_delivery
global cnsg_str # type: consignments
global random_str # type: random
global cal_eta_str # type: calendar
global buf_str # type: order_buffer
global sales_str # type: sales
global roe_str # type: roe

sdb.initiated = 'yes'

$procedure$
;

CREATE OR REPLACE PROCEDURE public.place_order_step1(IN sdb sys_dashboard, IN lc logistic_costs, IN buf order_buffer, IN cal_eta calendar)
 LANGUAGE hyperc
AS $procedure$

assert sdb.splited_proc == '-'
assert sdb.order_index <= 1 #QTY_of_possibles_orders
#assert lc.priority == sdb.current_delivery_type
global lc_str
global cal_eta_str
global buf_str

#assert sdb.PLANNING_FINISHED == True #Allow_more_than_1_order_per_time_if_commented
assert sdb.CURRENT_SOLD_ITEM == 1
lc_str = lc
assert cal_eta.WEEK_INDEX == sdb.CURRENT_CALCULATED_WEEK + lc_str.delivery_time
cal_eta_str = cal_eta

#create_new_delivery_in_buffer
assert buf.delivery_code == '-'
buf.delivery_code = lc_str.delivery_code
buf.SENT_WEEK_DATE = sdb.CURRENT_CALCULATED_DATE
buf.ETA_WEEK_DATE = cal_eta.WEEK_START_DATE
buf.consignment = sdb.CURRENT_CALCULATED_DATE
buf.counted = 'no'
buf_str = buf

sdb.splited_proc = 'place_order'
sdb.STEP = 21
sdb.current_delivery_type += 1

$procedure$
;

CREATE OR REPLACE PROCEDURE public.place_order_step21(IN sdb sys_dashboard, IN prods products, IN bxt box_templates, IN r roe)
 LANGUAGE hyperc
AS $procedure$

assert sdb.splited_proc == 'place_order'
assert sdb.STEP == 21
assert sdb.CURRENT_SOLD_ITEM <= sdb.ITEMS_COUNT
global bxt_str
global prods_str

assert prods.INDEX == sdb.CURRENT_SOLD_ITEM
assert bxt.ASIN == prods.ASIN
assert r.ASIN == prods.ASIN

if r.roe_consider == 'yes':
	bxt_str = bxt
	prods_str = prods
	sdb.STEP = 22

else:
	random_str.qty = 0
	sdb.STEP = 23

$procedure$
;

CREATE OR REPLACE PROCEDURE public.place_order_step22(IN sdb sys_dashboard, IN rnd random)
 LANGUAGE hyperc
AS $procedure$

assert sdb.splited_proc == 'place_order'
assert sdb.STEP == 22
global random_str

random_str = rnd
sdb.STEP = 23

$procedure$
;

CREATE OR REPLACE PROCEDURE public.place_order_step23(IN sdb sys_dashboard, IN in_deliv in_delivery)
 LANGUAGE hyperc
AS $procedure$
assert sdb.splited_proc == 'place_order'
assert sdb.STEP == 23

global in_deliv_str
global bxt_str
global lc_str
global prods_str
global buf_str
global cal_eta_str
global roe_str

if random_str.qty == 0 :
	sdb.STEP = 24
	
else:
	assert in_deliv.ASIN == '-'
	in_deliv.ASIN = prods_str.ASIN
	in_deliv.IN_DELIVERY_SENT_WEEK = sdb.CURRENT_CALCULATED_WEEK
	in_deliv.IN_DELIVERY_ETA_WEEK = cal_eta_str.WEEK_INDEX
	in_deliv.IN_DELIVERY_ETA_WEEK_START_DATE = cal_eta_str.WEEK_START_DATE
	in_deliv.IN_DELIVERY_SENT = sdb.CURRENT_CALCULATED_DATE
	in_deliv.IN_DELIVERY_ETA = cal_eta_str.WEEK_START_DATE
	in_deliv.PLAN_OR_FACT = 'PLAN'
	in_deliv.COUNTED = 'no'
	in_deliv.STATUS = 'open'
	in_deliv.consig = buf_str.consignment
	in_deliv.delivery_code = buf_str.delivery_code
	in_deliv.BOX_TEMPLATE = bxt_str.BOX_TEMPLATE
	in_deliv.QTY_IN_SINGLE_BOX = bxt_str.UNITS_PER_BOX
	in_deliv.BOXES_QTY = random_str.qty
	in_deliv.QTY = bxt_str.UNITS_PER_BOX * random_str.qty
	in_deliv.sum = in_deliv.QTY * prods_str.purchase_price
	in_deliv.weight = bxt_str.BOX_WEIGHT * in_deliv.BOXES_QTY
	in_deliv_str = in_deliv
	sdb.delivery_count += 1
	buf_str.TOTAL_VOLUME += (bxt_str.BOX_H * bxt_str.BOX_W * bxt_str.BOX_L)*in_deliv_str.BOXES_QTY
	buf_str.TOTAL_WEIGHT += bxt_str.BOX_WEIGHT*in_deliv_str.BOXES_QTY
	buf_str.TOTAL_QTY += bxt_str.UNITS_PER_BOX*in_deliv_str.BOXES_QTY
	sdb.STEP = 24
	
$procedure$
;

CREATE OR REPLACE PROCEDURE public.place_order_step24(IN sdb sys_dashboard, IN r roe, IN rep report, IN s sales, IN cal_now calendar)
 LANGUAGE hyperc
AS $procedure$
assert sdb.splited_proc == 'place_order'
assert sdb.STEP == 24
assert cal_now.WEEK_START_DATE == sdb.CURRENT_CALCULATED_DATE
global in_deliv_str
global prods_str
global roe_str

assert r.ASIN == prods_str.ASIN

if random_str.qty != 0 :
	
	#heuristic_limits_for_roe
	assert in_deliv_str.QTY >= s.QTY #min_limit.more_then_week_sales
	assert in_deliv_str.sum < (rep.profit*r.PERIOD)/(r.ROE_BENCHMARK)-(r.inventory_sum)	#max_limit_based_on_roe
	
	#Add_to_roe_table
	r.inventory_sum += in_deliv_str.sum
	r.INVENTORY += in_deliv_str.QTY
	
	#report_block
	assert rep.ASIN == prods_str.ASIN
	rep.SEND_TO_AMZ = in_deliv_str.QTY
	rep.PLAN_OR_FACT_ARRIVING = in_deliv_str.PLAN_OR_FACT
	#counting_how_much_times_need_to_receive_goods_in_future
	assert s.ASIN == prods_str.ASIN
	assert s.WEEK_START_DATE == in_deliv_str.IN_DELIVERY_ETA_WEEK_START_DATE
	s.RECEIVING_SHPMNTS_COUNT += 1
	
	#heuristic_limits_for_QTY
	#assert (r.INVENTORY - rep.SELL_PLAN*lc_str.delivery_time) <= 5*rep.SELL_PLAN
	
if sdb.CURRENT_SOLD_ITEM == sdb.ITEMS_COUNT:
	#exit_sku_ordering_cycle
	sdb.STEP = 3
	#counting_how_much_times_need_to_execute_logistic_efficiency_proc
	#cal_now.batches_qty += 1

else:
	#back_to_order_next_sku
	sdb.CURRENT_SOLD_ITEM += 1
	sdb.STEP = 21

$procedure$
;

CREATE OR REPLACE PROCEDURE public.place_order_step3(IN sdb sys_dashboard, IN cnsg consignments, IN buf order_buffer)
 LANGUAGE hyperc
AS $procedure$
global buf_str
global lc_str
assert sdb.splited_proc == 'place_order'
assert sdb.STEP == 3
if buf_str.TOTAL_QTY != 0:
	assert buf_str.TOTAL_WEIGHT >= lc_str.min_weight #KPI_from_logistic_limit
	global cnsg_str
	buf_str.DELIVERY_COST = buf_str.TOTAL_WEIGHT * lc_str.kg_price + lc_str.batch_registration_price
	assert cnsg.NAME == '-'
	cnsg.NAME = buf_str.consignment
	cnsg.COST_PER_KG = buf_str.DELIVERY_COST / buf_str.TOTAL_WEIGHT
	cnsg.COST_PER_UNIT = buf_str.DELIVERY_COST / buf_str.TOTAL_QTY
	cnsg.way_of_delivering = lc_str.way_of_delivering
	cnsg.company = lc_str.company
	cnsg.total_cost = buf_str.DELIVERY_COST
	cnsg.total_weight = buf_str.TOTAL_WEIGHT
	cnsg.total_volume = buf_str.TOTAL_VOLUME
	cnsg.delivery_code = buf_str.delivery_code
	cnsg_str = cnsg
	sdb.order_index += 1
	
else: #delete_row_in_buffer
	assert buf.delivery_code == buf_str.delivery_code
	assert buf.SENT_WEEK_DATE == buf_str.SENT_WEEK_DATE
	buf.delivery_code = '-'

sdb.STEP = 4

$procedure$
;

CREATE OR REPLACE PROCEDURE public.place_order_step4(IN sdb sys_dashboard, IN in_deliv in_delivery, IN r roe)
 LANGUAGE hyperc
AS $procedure$

assert sdb.splited_proc == 'place_order'
assert sdb.STEP == 4
assert sdb.delivery_count > sdb.delivery_counted
global buf_str
global lc_str

assert in_deliv.consig == buf_str.consignment
assert in_deliv.delivery_code == buf_str.delivery_code
assert in_deliv.STATUS == 'open'
assert r.ASIN == in_deliv.ASIN

#Add_delivery_cost
in_deliv.sum += buf_str.DELIVERY_COST * in_deliv.weight / buf_str.TOTAL_WEIGHT #ADD_delivery_cost
r.inventory_sum += buf_str.DELIVERY_COST * in_deliv.weight / buf_str.TOTAL_WEIGHT #ADD_delivery_cost

in_deliv.STATUS = 'close'
sdb.delivery_counted += 1

$procedure$
;

CREATE OR REPLACE PROCEDURE public.place_order_step4end(IN sdb sys_dashboard)
 LANGUAGE hyperc
AS $procedure$

assert sdb.splited_proc == 'place_order'
assert sdb.STEP == 4
assert sdb.delivery_count == sdb.delivery_counted

sdb.splited_proc = '-'
sdb.STEP = 0
sdb.CURRENT_SOLD_ITEM = 1
sdb.delivery_count = 0
sdb.delivery_counted = 0

$procedure$
;

CREATE OR REPLACE PROCEDURE public.receive_from_in_delivery_step1(IN prods products, IN sdb sys_dashboard, IN s sales)
 LANGUAGE hyperc
AS $procedure$

assert sdb.splited_proc == '-'

global prods_str
global sales_str

assert prods.INDEX == sdb.CURRENT_SOLD_ITEM
prods_str = prods
assert s.ASIN == prods.ASIN
assert s.WEEK_START_DATE == sdb.CURRENT_CALCULATED_DATE
assert sdb.SHIPMENTS_COUNT < s.RECEIVING_SHPMNTS_COUNT
sales_str = s

sdb.splited_proc = 'receive_from_in_delivery'
sdb.STEP = 2
$procedure$
;

CREATE OR REPLACE PROCEDURE public.receive_from_in_delivery_step2(IN sdb sys_dashboard, IN inv_stock inventory, IN rep report, IN in_deliv in_delivery, IN r roe)
 LANGUAGE hyperc
AS $procedure$

assert sdb.splited_proc == 'receive_from_in_delivery'
assert sdb.STEP == 2
global prods_str
global sales_str
assert in_deliv.IN_DELIVERY_ETA_WEEK_START_DATE == sdb.CURRENT_CALCULATED_DATE
assert in_deliv.ASIN == prods_str.ASIN
assert in_deliv.COUNTED == 'no'
assert inv_stock.ASIN == prods_str.ASIN
assert rep.ASIN == prods_str.ASIN
assert r.ASIN == prods_str.ASIN
rep.WEEK_START_DATE = sdb.CURRENT_CALCULATED_DATE
rep.PLAN_OR_FACT_ARRIVING = in_deliv.PLAN_OR_FACT
rep.QTY_ARRIVED_TO_AMZ += in_deliv.QTY #Collecting_all_receiving_goods,_summ_it_in_sell_procs_and_del_in_sell procs
sdb.ITEMS_IN_FC += in_deliv.QTY

if in_deliv.PLAN_OR_FACT == 'FACT':
	r.roe_consider = 'no'

#heuristic_try_dont_receive_goods_when_we_have_a_lot_in_wh
#assert inv_stock.QTY_STOCK <= sales_str.QTY*5

inv_stock.QTY_STOCK += in_deliv.QTY
inv_stock.sum_stock += in_deliv.sum
rep.aver_cost_income_batch = in_deliv.sum / in_deliv.QTY
inv_stock.aver_cost = inv_stock.sum_stock / inv_stock.QTY_STOCK
sdb.SHIPMENTS_COUNT += 1
in_deliv.COUNTED = 'yes'

sdb.splited_proc = '-'
sdb.STEP = 0
$procedure$
;

CREATE OR REPLACE PROCEDURE public.roe_calculation(IN prods products, IN sdb sys_dashboard, IN rep report, IN r roe)
 LANGUAGE hyperc
AS $procedure$
assert sdb.splited_proc == '-'
assert prods.INDEX == sdb.CURRENT_SOLD_ITEM
assert r.ASIN == prods.ASIN
assert r.CURRENT_PERIOD == r.PERIOD - 1
assert rep.ASIN == prods.ASIN
#r.roe_period = (prods.MARKUP * r.PERIOD * r.SALES)/(r.aver_inv)
r.roe_period = (r.profit_period*r.PERIOD)/(r.aver_inv_sum)
r.aver_inv = r.INVENTORY
r.aver_inv_sum = r.inventory_sum
r.SALES = rep.SELL_PLAN 
r.profit_period = rep.profit
if r.roe_consider == 'yes':
	assert r.roe_period >= r.ROE_BENCHMARK #Main_ROE_restriction_to_prevent_overstock
	r.CURRENT_PERIOD = 0
else:
	r.CURRENT_PERIOD = 0

rep.roe_period = r.roe_period
$procedure$
;

CREATE OR REPLACE PROCEDURE public.sell_item_allow_zero_step1(IN prods products, IN sdb sys_dashboard, IN inv_stock inventory, IN s sales, IN rep report, IN cal_now calendar, IN r roe)
 LANGUAGE hyperc
AS $procedure$
assert sdb.splited_proc == '-'
assert sdb.STEP == 0

global prods_str 
global cal_now_str 
global report_str 

#Join block
assert sdb.CURRENT_SOLD_ITEM <= sdb.ITEMS_COUNT
assert prods.INDEX == sdb.CURRENT_SOLD_ITEM
prods_str = prods
assert s.WEEK_START_DATE == sdb.CURRENT_CALCULATED_DATE
assert s.ASIN == prods_str.ASIN
assert sdb.SHIPMENTS_COUNT == s.RECEIVING_SHPMNTS_COUNT
assert inv_stock.ASIN == prods_str.ASIN
assert cal_now.WEEK_START_DATE == sdb.CURRENT_CALCULATED_DATE
cal_now_str = cal_now
assert r.ASIN == prods_str.ASIN
assert rep.ASIN == prods_str.ASIN
assert r.CURRENT_PERIOD < r.PERIOD - 1

#Logic block
days_period = prods_str.min_logistic_time*7+14
assert cal_now_str.DAYS_FROM_NOW <= days_period
if 	inv_stock.QTY_STOCK < s.QTY :				#sell_out_of_last_stock
	sdb.ITEMS_IN_FC -= inv_stock.QTY_STOCK
	rep.STOCK_IN_AMZ_BEGIN = inv_stock.QTY_STOCK
	rep.STOCK_IN_AMZ_BEGIN_SUM = inv_stock.sum_stock
	rep.LOST_SALES = s.QTY - inv_stock.QTY_STOCK
	rep.LOST_REVENUE = rep.LOST_SALES * prods_str.recom_retail_price
	rep.SELL_PLAN = inv_stock.QTY_STOCK
	s.revenue = rep.SELL_PLAN * prods_str.recom_retail_price
	rep.revenue = s.revenue 
	s.profit = s.revenue - rep.SELL_PLAN * inv_stock.aver_cost
	rep.profit = s.profit
	inv_stock.QTY_STOCK -= inv_stock.QTY_STOCK
	inv_stock.sum_stock -= inv_stock.sum_stock
	r.INVENTORY -= rep.SELL_PLAN
	r.inventory_sum -= rep.SELL_PLAN * inv_stock.aver_cost
	rep.STOCK_IN_AMZ_END = inv_stock.QTY_STOCK
	rep.STOCK_IN_AMZ_END_SUM = inv_stock.sum_stock
	r.aver_inv += r.INVENTORY
	r.aver_inv_sum += r.inventory_sum
	#r.roe_week = (prods_str.MARKUP * rep.SELL_PLAN)/(r.INVENTORY) #Based_on_qty
	if s.profit/r.inventory_sum > 0 :
		r.roe_week = r.PERIOD * s.profit/r.inventory_sum #Based_on_inventory_sum
	else:
		r.roe_week = 0
	r.SALES += rep.SELL_PLAN
	r.profit_period += s.profit
	
else: 	
	sdb.ITEMS_IN_FC -= s.QTY
	rep.STOCK_IN_AMZ_BEGIN = inv_stock.QTY_STOCK
	rep.STOCK_IN_AMZ_BEGIN_SUM = inv_stock.sum_stock
	rep.LOST_SALES = 0
	rep.LOST_REVENUE = 0
	inv_stock.QTY_STOCK -= s.QTY
	inv_stock.sum_stock -= s.QTY * inv_stock.aver_cost
	r.INVENTORY -= rep.SELL_PLAN
	r.inventory_sum -= rep.SELL_PLAN * inv_stock.aver_cost
	rep.SELL_PLAN = s.QTY
	s.revenue = rep.SELL_PLAN * prods_str.recom_retail_price
	rep.revenue = s.revenue
	s.profit = s.revenue - rep.SELL_PLAN * inv_stock.aver_cost
	rep.profit = s.profit
	rep.STOCK_IN_AMZ_END = inv_stock.QTY_STOCK
	rep.STOCK_IN_AMZ_END_SUM = inv_stock.sum_stock
	r.aver_inv += r.INVENTORY
	r.aver_inv_sum += r.inventory_sum
	#r.roe_week = (prods_str.MARKUP * rep.SELL_PLAN)/(r.INVENTORY) #Based_on_qty
	if s.profit/r.inventory_sum > 0 :
		r.roe_week = r.PERIOD * s.profit/r.inventory_sum #Based_on_inventory_sum
	else:
		r.roe_week = 0
	r.SALES += rep.SELL_PLAN
	r.profit_period += s.profit

rep.PRODUCT = prods_str.SKU
rep.WEEK_NUMBER = sdb.CURRENT_CALCULATED_WEEK
rep.PROD_INDEX = sdb.CURRENT_SOLD_ITEM
rep.WEEK_START_DATE = sdb.CURRENT_CALCULATED_DATE
rep.INVENTORY_UNITS = r.INVENTORY
rep.inv_sum = r.inventory_sum
rep.ROE = r.roe_week
report_str = rep
r.CURRENT_PERIOD += 1
sdb.splited_proc = 'sell_item'
sdb.STEP = 2

$procedure$
;

CREATE OR REPLACE PROCEDURE public.sell_item_step1(IN prods products, IN sdb sys_dashboard, IN inv_stock inventory, IN s sales, IN rep report, IN cal_now calendar, IN r roe)
 LANGUAGE hyperc
AS $procedure$

global prods_str 
global cal_now_str 
global report_str 

assert sdb.splited_proc == '-'
assert sdb.STEP == 0

#Join block
assert sdb.CURRENT_SOLD_ITEM <= sdb.ITEMS_COUNT
assert prods.INDEX == sdb.CURRENT_SOLD_ITEM
prods_str = prods
assert s.WEEK_START_DATE == sdb.CURRENT_CALCULATED_DATE
assert s.ASIN == prods_str.ASIN
assert sdb.SHIPMENTS_COUNT == s.RECEIVING_SHPMNTS_COUNT
assert inv_stock.ASIN == prods_str.ASIN
assert cal_now.WEEK_START_DATE == sdb.CURRENT_CALCULATED_DATE
cal_now_str = cal_now
assert r.ASIN == prods_str.ASIN
assert rep.ASIN == prods_str.ASIN
assert r.CURRENT_PERIOD < r.PERIOD - 1 

#Logic block
days_period = prods_str.min_logistic_time*7+14
assert cal_now_str.DAYS_FROM_NOW > days_period
assert inv_stock.QTY_STOCK >= s.QTY #Key_restriction_that_prevents_stock_cross_zero
	
sdb.ITEMS_IN_FC -= s.QTY
rep.STOCK_IN_AMZ_BEGIN = inv_stock.QTY_STOCK
rep.STOCK_IN_AMZ_BEGIN_SUM = inv_stock.sum_stock
rep.LOST_SALES = 0
rep.LOST_REVENUE = 0
inv_stock.QTY_STOCK -= s.QTY
inv_stock.sum_stock -= s.QTY * inv_stock.aver_cost
r.INVENTORY -= rep.SELL_PLAN
r.inventory_sum -= rep.SELL_PLAN * inv_stock.aver_cost
rep.SELL_PLAN = s.QTY
s.revenue = rep.SELL_PLAN * prods_str.recom_retail_price
rep.revenue = s.revenue
s.profit = s.revenue - rep.SELL_PLAN * inv_stock.aver_cost
rep.profit = s.profit
rep.STOCK_IN_AMZ_END = inv_stock.QTY_STOCK
rep.STOCK_IN_AMZ_END_SUM = inv_stock.sum_stock
r.aver_inv += r.INVENTORY
r.aver_inv_sum += r.inventory_sum
#r.roe_week = (prods_str.MARKUP * rep.SELL_PLAN)/(r.INVENTORY) #Based_on_qty
if s.profit/r.inventory_sum > 0 :
	r.roe_week = r.PERIOD * s.profit/r.inventory_sum #Based_on_inventory_sum
else:
	r.roe_week = 0

r.SALES += rep.SELL_PLAN
r.profit_period += s.profit

rep.PRODUCT = prods_str.SKU
rep.WEEK_NUMBER = sdb.CURRENT_CALCULATED_WEEK
rep.PROD_INDEX = sdb.CURRENT_SOLD_ITEM
rep.WEEK_START_DATE = sdb.CURRENT_CALCULATED_DATE
rep.INVENTORY_UNITS = r.INVENTORY
rep.inv_sum = r.inventory_sum
rep.ROE = r.roe_week
report_str = rep
r.CURRENT_PERIOD += 1
sdb.splited_proc = 'sell_item'
sdb.STEP = 2

$procedure$
;

CREATE OR REPLACE PROCEDURE public.sell_item_step2(IN sdb sys_dashboard, IN rep report, IN rpte report_export, IN r roe)
 LANGUAGE hyperc
AS $procedure$

assert sdb.splited_proc == 'sell_item'
assert sdb.STEP == 2

global report_str

#Report block
assert rep.ASIN == report_str.ASIN
assert rpte.ASIN == report_str.ASIN
assert r.ASIN == report_str.ASIN
assert r.CURRENT_PERIOD_storage < r.PERIOD_storage - 1
rpte.WEEK_NUMBER = report_str.WEEK_NUMBER
rpte.WEEK_START_DATE = report_str.WEEK_START_DATE
rpte.ASIN = report_str.ASIN
rpte.PRODUCT = report_str.PRODUCT
rpte.SELL_PLAN = report_str.SELL_PLAN
rpte.STOCK_IN_AMZ_END = report_str.STOCK_IN_AMZ_END
rpte.PLACE_ORDER = report_str.PLACE_ORDER
rpte.SEND_TO_AMZ = report_str.SEND_TO_AMZ
rpte.PROD_INDEX = report_str.PROD_INDEX
rpte.LOST_SALES = report_str.LOST_SALES
rpte.STOCK_IN_AMZ_BEGIN = report_str.STOCK_IN_AMZ_BEGIN
rpte.QTY_ARRIVED_TO_AMZ = report_str.QTY_ARRIVED_TO_AMZ
rpte.PLAN_OR_FACT_ARRIVING = report_str.PLAN_OR_FACT_ARRIVING
rpte.ROE = report_str.ROE * 4
rpte.INVENTORY_UNITS = report_str.INVENTORY_UNITS
rpte.inv_sum = report_str.inv_sum
rpte.roe_period = report_str.roe_period
rpte.revenue = report_str.revenue
rpte.profit = report_str.profit
rpte.STOCK_IN_AMZ_BEGIN_SUM = report_str.STOCK_IN_AMZ_BEGIN_SUM
rpte.STOCK_IN_AMZ_END_SUM = report_str.STOCK_IN_AMZ_END_SUM
rpte.LOST_REVENUE = report_str.LOST_REVENUE
if report_str.profit / report_str.revenue > 0 : #if_delete_if_will_not_work
	rpte.margin = report_str.profit / report_str.revenue
else :
	rpte.margin = 0
rpte.aver_cost_income_batch = report_str.aver_cost_income_batch
rpte.storage_upcost = rep.storage_upcost

sdb.SHIPMENTS_COUNT = 0	#need_receive_from_in_delivery 
rep.SEND_TO_AMZ = 0
rep.QTY_ARRIVED_TO_AMZ = 0
rep.PLAN_OR_FACT_ARRIVING = '-'
rep.aver_cost_income_batch = 0
rep.storage_upcost = 0
rep.cum_sum_inv_units += report_str.STOCK_IN_AMZ_BEGIN
sdb.PLANNING_FINISHED = True

if r.roe_week >= r.ROE_BENCHMARK:
	r.roe_consider = 'yes'

#Counters block
sdb.CURRENT_SOLD_ITEM += 1
r.CURRENT_PERIOD_storage += 1
sdb.splited_proc = '-'
sdb.STEP = 0

$procedure$
;

CREATE OR REPLACE PROCEDURE public.storage_calculation(IN prods products, IN sdb sys_dashboard, IN rep report, IN r roe, IN inv inventory)
 LANGUAGE hyperc
AS $procedure$
assert sdb.splited_proc == '-'
assert prods.INDEX == sdb.CURRENT_SOLD_ITEM
assert r.ASIN == prods.ASIN
assert r.CURRENT_PERIOD_storage == r.PERIOD_storage - 1
assert rep.ASIN == prods.ASIN
assert inv.ASIN == prods.ASIN
rep.storage_upcost = (rep.cum_sum_inv_units/r.PERIOD_storage) * prods.unit_storage_cost
rep.cum_sum_inv_units = rep.STOCK_IN_AMZ_BEGIN
r.CURRENT_PERIOD_storage = 0
r.inventory_sum += rep.storage_upcost
inv.sum_stock += rep.storage_upcost
$procedure$
;

