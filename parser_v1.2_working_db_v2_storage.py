
REMOTE_USERNAME = 'anton'
DATABASE = 'working_db_v2_storage'
RSA_file = r'./id_rsa'
PORT=18494


import re
#from tkinter import *
#from tkinter import messagebox 
#from tkinter.ttk import Progressbar
#import shutil
#import time
import warnings
import os
from os import chdir
from os import path
import pandas as pd
import numpy as np
#import datetime as dt
#from datetime import datetime, timedelta
from sshtunnel import SSHTunnelForwarder
import psycopg2
import psycopg2.extras as extras
absFilePath = os.path.abspath(__file__)
os.chdir( os.path.dirname(absFilePath) )

REMOTE_HOST = 'hcc1.sshto.net'
REMOTE_SSH_PORT = 22
USER = 'postgres'
warnings.filterwarnings('ignore')
sqlreq = '''
TRANSIT UPDATE sys_dashboard SET "CURRENT_CALCULATED_WEEK" = 8;
'''
hc_plan_query = '''
with 
	last_plan as 
	(select 
	max(created_time) as last_datetime
	from hc_plan
	)
Select * 
from hc_plan 
join last_plan lp on lp.last_datetime = hc_plan.created_time
order by step_num
'''


def parser(table, data):
    sub1 = data[data.find('output_parameter'):]
    sub2 = sub1[sub1.find(f'"{table}": ')+5+len(table):]
    sub2 = sub2[:sub2.find('},')] #here is raw string of table from report
    cols = re.split('\,\s', re.sub('"', '', re.sub(':\s[^\,]+', '', sub2)))
    values = re.split('\,\s', re.sub('}', '', re.sub('"', '', re.sub('"\w+\"\:\s', '', sub2))))
    df = pd.DataFrame(list(zip(cols,values))).transpose()
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    return df

print("Getting results")
with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
         ssh_username = REMOTE_USERNAME,
         ssh_pkey = RSA_file, #r"C:/Users/golan/.ssh/id_rsa",
         remote_bind_address=('localhost', PORT),
         local_bind_address=('localhost', PORT)):
     conn = psycopg2.connect(dbname=DATABASE, user=USER, password='', host='localhost', port=PORT)
     result = pd.read_sql(hc_plan_query, conn)
     conn.close()

def get_report_from_sell_procedures ():
    
    df_for_parsing = result.loc[(result['proc_name'] == 'sell_item_step2') | (result['proc_name'] == 'kpi_sell_item_step2')].reset_index()
    r = len(df_for_parsing.index)
    i=0
    while i<r :
        if i<1 :
            tt = df_for_parsing.iloc[i][['data']]
            tt2 = tt.values.tolist()
            report_sales = parser('rpte', str(tt2[0]).replace("'", '"'))
        else:
            tt = df_for_parsing.iloc[i][['data']]
            tt2 = tt.values.tolist()
            report_sales = pd.concat([report_sales, parser('rpte', str(tt2[0]).replace("'", '"'))])
        i +=1
    print('report table from sell procedures ready')
    report_sales.to_excel(f'{DATABASE}_report_from_sales.xlsx', index=False)
    return report_sales

def get_table_from_proc (table, proc_name):
    #table = 'consignments'
    #proc_name = 'logistic_efficiency'
    df_for_parsing = result.loc[result['proc_name'] == proc_name].reset_index()
    r = len(df_for_parsing.index)
    i=0
    while i<r :
        if i<1 :
            tt = df_for_parsing.iloc[i][['data']]
            tt2 = tt.values.tolist()
            out = parser(table, str(tt2[0]).replace("'", '"'))
        else:
            tt = df_for_parsing.iloc[i][['data']]
            tt2 = tt.values.tolist()
            out = pd.concat([out, parser(table, str(tt2[0]).replace("'", '"'))])
        i +=1
    print(f'{table} from {proc_name} procedure ready')
    out.to_excel(f'{DATABASE}_{table}_from_{proc_name}.xlsx', index=False)
    return out


#load tables
get_report_from_sell_procedures ()
get_table_from_proc ('cnsg', 'place_order_step3')
in_deliv = get_table_from_proc ('in_deliv', 'place_order_step23')
with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
         ssh_username = REMOTE_USERNAME,
         ssh_pkey = RSA_file, #r"/id_rsa",
         remote_bind_address=('localhost', PORT),
         local_bind_address=('localhost', PORT)):
     conn = psycopg2.connect(dbname=DATABASE, user=USER, password='', host='localhost', port=PORT)
     result = pd.read_sql(hc_plan_query, conn)
     conn.close()

with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
         ssh_username = REMOTE_USERNAME,
         ssh_pkey = RSA_file, # r"/id_rsa",
         remote_bind_address=('localhost', PORT),
         local_bind_address=('localhost', PORT)):
     conn = psycopg2.connect(dbname=DATABASE, user=USER, password='', host='localhost', port=PORT)
     products = pd.read_sql('select * from products', conn)
     conn.close()

with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
         ssh_username = REMOTE_USERNAME,
         ssh_pkey = RSA_file, # r"/id_rsa",
         remote_bind_address=('localhost', PORT),
         local_bind_address=('localhost', PORT)):
     conn = psycopg2.connect(dbname=DATABASE, user=USER, password='', host='localhost', port=PORT)
     box_templates = pd.read_sql('select * from box_templates', conn)
     conn.close()

def report_alpha() :
    #Preparing report 1
    report_sales = get_report_from_sell_procedures ()
    cnsg = get_table_from_proc ('cnsg', 'place_order_step3')
    cnsg['consig'] = cnsg['NAME']
    in_deliv = get_table_from_proc ('in_deliv', 'place_order_step23')
    in_deliv['k'] = 1
    in_deliv = in_deliv.sort_values(by=['consig', 'ASIN', 'delivery_code', 'QTY'], ascending=False)
    in_deliv['ks'] = in_deliv.groupby(['consig', 'ASIN', 'delivery_code'])['k'].cumsum()
    in_deliv = in_deliv[in_deliv['ks'] == 1]
    del in_deliv['k']
    del in_deliv['ks']
    in_deliv = in_deliv.merge(products, how="inner", on=['ASIN'])
    box_templates['template_number'] = box_templates['idx']
    in_deliv = in_deliv.merge(box_templates[['BOX_TEMPLATE', 'template_number', 'BOX_WEIGHT', 'UNITS_PER_BOX', 'ASIN']], how="left", on=['BOX_TEMPLATE', 'ASIN'])
    cnsg['delivery_code'] = cnsg['company'] + cnsg['way_of_delivering']
    in_deliv = in_deliv.merge(cnsg, how="left", on=['consig', 'delivery_code'])
    in_deliv['type'] = 'boxes'
    in_deliv['finish_period'] = max(report_sales['WEEK_START_DATE'])
    in_deliv['fc_limit'] = '4782 in dev'
    in_deliv['max_weightcost'] = '0.5 in dev'
    in_deliv['Ship mode'] = in_deliv['delivery_code']
    in_deliv['date_eta'] = in_deliv['IN_DELIVERY_ETA_WEEK_START_DATE']
    in_deliv['date_sent'] = in_deliv['IN_DELIVERY_SENT']
    in_deliv['wfrom'] = 'HQ in dev'
    in_deliv['wto'] = 'AZFC in dev'
    in_deliv['msku'] = 'msku'
    in_deliv['weight'] = in_deliv['BOX_WEIGHT'].astype(int) * in_deliv['BOXES_QTY'].astype(int)
    in_deliv['qty'] = in_deliv['QTY_IN_SINGLE_BOX'].astype(int) * in_deliv['BOXES_QTY'].astype(int)
    in_deliv['boxes_qty'] = in_deliv['IN_DELIVERY_SENT']
    in_deliv['warehouse_id'] = 'AZFC in dev'
    in_deliv['date'] = ''
    in_deliv['sku_stored'] = ''
    in_deliv['num week'] = in_deliv['IN_DELIVERY_SENT_WEEK']
    in_deliv['qty_eta'] = ''
    in_deliv['availibale_amz'] = ''
    in_deliv['reserved(amz)'] = ''
    in_deliv['plan_id'] = str(result['plan_id'].drop_duplicates().to_list()[0])
    in_deliv['sales_per_week'] = ''
    in_deliv['utilization_qty'] = ''
    in_deliv_insert = in_deliv[['type', 'SKU', 'consig', 'finish_period', 'fc_limit', 'max_weightcost', 'Ship mode', 'date_eta', 'date_sent', 'wfrom',
    'wto', 'template_number', 'BOX_TEMPLATE', 'BOXES_QTY','msku', 'total_cost', 'weight', 'UNITS_PER_BOX', 'SKU', 'qty','warehouse_id', 
    'date', 'sku_stored', 'num week', 'qty_eta', 'availibale_amz', 'reserved(amz)', 'plan_id', 'sales_per_week', 'utilization_qty']]
    in_deliv_insert.columns = ['type', 'Product Name', 'id', 'finish_period', 'fc_limit', 'max_weightcost', 'Ship mode', 'date_eta', 'date_sent', 'wfrom', 'wto', 'template_number', 'box_template', 'boxes_qty', 'msku', 'cost', 'weight', 'qty_in_box', 'sku', 'qty', 'warehouse_id', 'date', 'sku_stored', 'num week', 'qty_eta', 'availibale_amz', 'reserved(amz)', 'plan_id', 'sales_per_week', 'utilization_qty']


    #Preparing report 2
    report_sales = get_report_from_sell_procedures ()
    report_sales = report_sales.merge(in_deliv[['ASIN', 'IN_DELIVERY_ETA_WEEK_START_DATE', 'consig', 'BOX_TEMPLATE', 'boxes_qty', 'total_cost', 
    'weight', 'QTY_IN_SINGLE_BOX', 'qty', 'plan_id']], how="left", left_on=['ASIN', 'WEEK_START_DATE'], right_on=['ASIN', 'IN_DELIVERY_ETA_WEEK_START_DATE'])
    report_sales['type'] = 'boxes'
    report_sales['prod'] = ''
    report_sales['id'] = report_sales['consig']
    report_sales['finish_period'] = max(report_sales['WEEK_START_DATE'])
    report_sales['fc_limit'] = '4782 in dev'
    report_sales['max_weightcost'] = '0.5 in dev'
    report_sales['Ship mode'] = ' '
    report_sales['date_eta'] = '-'
    report_sales['date_sent'] = '-'
    report_sales['wfrom'] = '-'
    report_sales['wto'] = '-'
    report_sales['template_number'] = '-'
    report_sales['msku'] = '-'
    report_sales['sku1'] = '-'
    report_sales['qty1'] = '-'
    report_sales['warehouse_id'] = 'AZFC'
    report_sales['availibale_amz'] = report_sales['STOCK_IN_AMZ_BEGIN']
    report_sales['reserved(amz)'] = ' '
    report_sales['utilization_qty'] = ' '

    report_sales_to_report = report_sales[['type', 'prod', 'id', 'finish_period', 'fc_limit', 'max_weightcost', 'Ship mode', 
    'date_eta', 'date_sent', 'wfrom', 'wto', 'template_number', 'BOX_TEMPLATE', 'boxes_qty', 'msku', 'total_cost', 'weight', 'QTY_IN_SINGLE_BOX', 'sku1',
    'qty1', 'warehouse_id', 'WEEK_START_DATE', 'PRODUCT', 'WEEK_NUMBER', 'QTY_ARRIVED_TO_AMZ', 'availibale_amz', 'reserved(amz)', 'plan_id', 'SELL_PLAN', 'utilization_qty']]

    report_sales_to_report.columns = ['type', 'Product Name', 'id', 'finish_period', 'fc_limit', 'max_weightcost', 'Ship mode',
    'date_eta', 'date_sent', 'wfrom', 'wto', 'template_number', 'box_template', 'boxes_qty', 'msku', 'cost', 'weight', 'qty_in_box',
    'sku', 'qty', 'warehouse_id', 'date', 'sku_stored', 'num week', 'qty_eta', 'availibale_amz', 'reserved(amz)', 'plan_id',
    'sales_per_week', 'utilization_qty']

    in_deliv_insert = pd.concat([in_deliv_insert, report_sales_to_report])
    in_deliv_insert.to_excel(f'{DATABASE}_report_alpha.xlsx', index=False)

    print(f'{DATABASE}_report_alpha.xlsx saved')

report_alpha()