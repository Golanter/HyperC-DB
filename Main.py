weeks_number = 16
start_date = "09/05/22" #"%d/%m/%y"

import pathlib
pathlib.Path().resolve()
from tkinter import *
from tkinter import messagebox 
from tkinter.ttk import Progressbar
import datetime as dt
import shutil
import time
import warnings
from os import chdir
from os import path
import pandas as pd
import os
import numpy as np
import datetime
from sshtunnel import SSHTunnelForwarder
import psycopg2
import psycopg2.extras as extras
from datetime import datetime, timedelta
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
absFilePath = os.path.abspath(__file__)
os.chdir( os.path.dirname(absFilePath) )

#PORT=18494
REMOTE_HOST = 'hcc1.sshto.net'
REMOTE_SSH_PORT = 22
#REMOTE_USERNAME = 'anton'
RSA_file = 'id_rsa'
#DATABASE = 'anton_practice'
USER = 'postgres'
local_bind_host = 'localhost'
local_bind_port = 18494
warnings.filterwarnings('ignore')

print(os.getcwd())
print(datetime.strptime(start_date, "%d/%m/%y").date())
first_week_date = datetime.strptime(start_date, "%d/%m/%y").date()

random_t = '''
insert into "public"."random" ("qty") values (0);
insert into "public"."random" ("qty") values (1);
insert into "public"."random" ("qty") values (2);
insert into "public"."random" ("qty") values (3);
insert into "public"."random" ("qty") values (4);
insert into "public"."random" ("qty") values (5);
insert into "public"."random" ("qty") values (6);
insert into "public"."random" ("qty") values (7);
insert into "public"."random" ("qty") values (8);
insert into "public"."random" ("qty") values (9);
insert into "public"."random" ("qty") values (10);
insert into "public"."random" ("qty") values (14);
insert into "public"."random" ("qty") values (18);
insert into "public"."random" ("qty") values (22);
insert into "public"."random" ("qty") values (26);
insert into "public"."random" ("qty") values (34);
insert into "public"."random" ("qty") values (38);
insert into "public"."random" ("qty") values (42);
insert into "public"."random" ("qty") values (46);
insert into "public"."random" ("qty") values (54);
insert into "public"."random" ("qty") values (58);
insert into "public"."random" ("qty") values (62);
insert into "public"."random" ("qty") values (66);
insert into "public"."random" ("qty") values (72);
insert into "public"."random" ("qty") values (76);
insert into "public"."random" ("qty") values (84);
insert into "public"."random" ("qty") values (88);
insert into "public"."random" ("qty") values (92);
insert into "public"."random" ("qty") values (96);
insert into "public"."random" ("qty") values (40);
insert into "public"."random" ("qty") values (50);
insert into "public"."random" ("qty") values (100);
insert into "public"."random" ("qty") values (200);
insert into "public"."random" ("qty") values (300);
'''

def execute_values(conn, df, table):
    """
    Using psycopg2.extras.execute_values() to insert the dataframe
    """
    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in df.to_numpy()]
    # Comma-separated dataframe columns
    df1=df.columns.to_list()
    i = 0
    while i < len(df1):
        df1[i] = '"'+df1[i]+'"'
        i += 1
    cols = ', '.join(df1)
    #cols = ', '.join(list(df.columns))
    # SQL quert to execute
    query  = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    #query  = "INSERT INTO %s VALUES %%s" % (table, cols)
    cursor = conn.cursor()
    try:
        print(query)
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("execute_values() done")
    cursor.close()

def run():
    global bar
    prepare_calendar()
    bar['value'] = 20
    window.update()
    load_calendar()
    bar['value'] = 30
    lbl3 = Label(window, text="Logistic costs loading", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=7)
    load_logistic_costs()
    bar['value'] = 30
    lbl3 = Label(window, text="Products loading", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=7)
    window.update()
    load_products()
    bar['value'] = 40
    lbl3 = Label(window, text="in_delivery loading", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=8)
    window.update()
    prepare_in_delivery()
    bar['value'] = 70
    lbl3 = Label(window, text="inventory loading", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=10)
    window.update()
    prepare_inventory()
    bar['value'] = 60
    lbl3 = Label(window, text="roe loading", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=9)
    window.update()
    update_roe()
    bar['value'] = 80
    lbl3 = Label(window, text="sales loading", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=11)
    window.update()
    prepare_sales()
    bar['value'] = 90
    lbl3 = Label(window, text="box_templates loading", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=12)
    window.update()
    prepare_box_templates()
    prepare_consig_reports_random_buffer()
    bar['value'] = 95
    #lbl3 = Label(window, text="Saving files", font=("Arial Bold", 12))
    #lbl3.grid(column=0, row=13)
    window.update()
    #save()
    bar['value'] = 100
    lbl3 = Label(window, text="DONE!!!", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=14)
    window.update()

def clicked_refill():
    global DATABASE
    DATABASE = database.get()
    global REMOTE_USERNAME
    REMOTE_USERNAME = usernameform.get()
    global PORT
    PORT = int(portform.get())

    global lbl3
    lbl3 = Label(window, text="Parsing excel file", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=4)
    #lbl.configure(text="Parsing excel file")
    try:
        global Denorm_table
        Denorm_table = pd.read_excel(r'./Source.xlsm', header=1)
    except: 
        messagebox.showinfo('Error loading "Source.xlsm"')
    
    try:
        global products_table
        products_table = Denorm_table[['ASIN', 'SKU', 'DESCRIPTION', 'PRODUCT_CATEGORY_NAME', 'STATUS', 'MINIMUM_SAFETY_QTY', 'TYP_TIME_WH_FC1', 'MOQ', 'recom_retail_price', 'purchase_price']]
        products_table['DESCRIPTION'] = products_table['DESCRIPTION'].replace(np.nan, '-')
        products_table['PRODUCT_CATEGORY_NAME'] = products_table['PRODUCT_CATEGORY_NAME'].replace(np.nan, '-')
        products_table['STATUS'] = products_table['STATUS'].replace(np.nan, '-')
        products_table['MOQ'] = products_table['MOQ'].replace(np.nan, 1).astype(int)
        products_table = products_table.rename(columns={"TYP_TIME_WH_FC1" : "LEAD_TIME"})
        products_table['MINIMUM_SAFETY_QTY'] = products_table['MINIMUM_SAFETY_QTY'].astype(int)
        products_table['LEAD_TIME'] = products_table['LEAD_TIME'].astype(int)
        products_table['LEAD_TIME_WEEKS'] = (products_table['LEAD_TIME']/7).apply(np.ceil).astype(int)
        products_table['recom_retail_price'] = products_table['recom_retail_price'].astype(float)
        products_table['purchase_price'] = products_table['purchase_price'].astype(float)
    except: 
        messagebox.showinfo('Error during parsing products')

    global bar
    bar = Progressbar(window, length=200)
    bar.grid(column=0, row=3)
    bar['value'] = 10
    run()

def clicked_new():
    global DATABASE
    DATABASE = database.get()
    global REMOTE_USERNAME
    REMOTE_USERNAME = usernameform.get()
    global PORT
    PORT = int(portform.get())
    create_init_db()
    #lbl.configure(text="Parsing excel file")
      
    global bar
    bar = Progressbar(window, length=200)
    bar.grid(column=0, row=3)
    bar['value'] = 10
    create_tables()
    
def create_tables():
    try:
        with open(r'./tables.sql', mode='r') as buf:
            tables = buf.read()
        with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
             ssh_username=REMOTE_USERNAME,
             ssh_pkey = "./id_rsa",
             remote_bind_address=('localhost', PORT),
             local_bind_address=('localhost', PORT)):
         conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
         conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
         cur = conn.cursor()
         cur.execute(tables)
         conn.commit()
         cur.close()
         conn.close()
        print('Tables created from file')
        lbl3 = Label(window, text=f'Tables created from file.', font=("Arial Bold", 12))
        lbl3.grid(column=1, row=6)
    except:
        print('Error during creating tables')
        lbl3 = Label(window, text=f'Error during creating tables.', font=("Arial Bold", 12))
        lbl3.grid(column=1, row=6)
    create_procedures()

def create_procedures():
    try:
        with open(r'./procedures.sql', mode='r') as buf:
            procedures = buf.read()
        with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
             ssh_username=REMOTE_USERNAME,
             ssh_pkey = r"./id_rsa",
             remote_bind_address=('localhost', PORT),
             local_bind_address=('localhost', PORT)):
         conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
         conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
         cur = conn.cursor()
         cur.execute(procedures)
         conn.commit()
         cur.close()
         conn.close()
        print('Procedures created from file')
        lbl3 = Label(window, text=f'Procedures created from file.', font=("Arial Bold", 12))
        lbl3.grid(column=1, row=7)
    except:
        print('Error during creating Procedures')
        lbl3 = Label(window, text=f'Error during creating Procedures.', font=("Arial Bold", 12))
        lbl3.grid(column=1, row=7)
    clicked_refill()
#Call_clicked_refill

def load_logistic_costs():
    try:
        global logistic_costs
        logistic_costs = pd.read_excel('logistic_costs.xlsx', header=0)
    except: 
        messagebox.showinfo('Error loading "logistic_costs.xlsx"')
    try:
        logistic_costs['company'] = logistic_costs['company'].astype(str)
        logistic_costs['way_of_delivering'] = logistic_costs['way_of_delivering'].astype(str)
        logistic_costs['kg_price'] = logistic_costs['kg_price'].astype(float)
        logistic_costs['value_weight'] = logistic_costs['value_weight'].astype(float)
        logistic_costs['batch_registration_price'] = logistic_costs['batch_registration_price'].astype(float)
        logistic_costs['min_volume'] = logistic_costs['min_volume'].astype(float)
        logistic_costs['max_volume'] = logistic_costs['max_volume'].astype(float)
        logistic_costs['max_weight'] = logistic_costs['max_weight'].astype(float)
        logistic_costs['kg_cost_benchmark'] = logistic_costs['kg_cost_benchmark'].astype(float)
        logistic_costs['delivery_time'] = logistic_costs['delivery_time'].astype(int)
        logistic_costs['delivery_code'] = logistic_costs['delivery_code'].astype(str)
        logistic_costs['min_weight'] = logistic_costs['min_weight'].astype(float)
        try: 
            del logistic_costs['idx']
        except:
            print('already no idx, ok')
    except: 
        messagebox.showinfo('Error during parsing logistic_costs.xlsx')
    try: 
        with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
             ssh_username=REMOTE_USERNAME,
             ssh_pkey = r"./id_rsa",
             remote_bind_address=('localhost', PORT),
             local_bind_address=('localhost', PORT)):
         conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
         cur = conn.cursor()
         cur.execute('DELETE FROM "public"."logistic_costs";')
         conn.commit()
         cur.close()
         conn.close()
        print("Table logistic_costs cleaned") 
    except:
        print('lc doesnt exist')
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
             ssh_username=REMOTE_USERNAME,
             ssh_pkey = r"./id_rsa",
             remote_bind_address=('localhost', PORT),
             local_bind_address=('localhost', PORT)):
         conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
         execute_values(conn, logistic_costs.astype(str), 'logistic_costs')
         conn.close()
    print("logistic_costs refilled")
    lbl3 = Label(window, text="logistic_costs loaded", font=("Arial Bold", 12))
    lbl3.grid(column=1, row=7)

def create_init_db():
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
         ssh_username=REMOTE_USERNAME,
         ssh_pkey = r"./id_rsa",
         remote_bind_address=('localhost', PORT),
         local_bind_address=('localhost', PORT)):
     conn = psycopg2.connect(dbname = 'init', user = USER, password='', host='localhost', port=PORT)
     conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
     cur = conn.cursor()
     cur.execute(f'create database {DATABASE};')
     conn.commit()
     cur.close()
     conn.close()
    print("DB created")
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
         ssh_username=REMOTE_USERNAME,
         ssh_pkey = r"./id_rsa",
         remote_bind_address=('localhost', PORT),
         local_bind_address=('localhost', PORT)):
     conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
     conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
     cur = conn.cursor()
     cur.execute(f'TRANSIT INIT;')
     conn.commit()
     cur.close()
     conn.close()
    global lbl3
    lbl3 = Label(window, text=f'DB {DATABASE} created, hyperc_transit initiated.', font=("Arial Bold", 12))
    lbl3.grid(column=1, row=4)
    try:
        with open(r'./hyperc_transit.sql', mode='r') as buf:
            hyperc_transit = buf.read()
        print('Transit file from directory loaded')
        with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
             ssh_username=REMOTE_USERNAME,
             ssh_pkey = r"./id_rsa",
             remote_bind_address=('localhost', PORT),
             local_bind_address=('localhost', PORT)):
         conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
         conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
         cur = conn.cursor()
         cur.execute(hyperc_transit)
         conn.commit()
         cur.close()
         conn.close()
        print('Transit from directory updated')
        lbl3 = Label(window, text=f'hyperc_transit updated from directory.', font=("Arial Bold", 12))
        lbl3.grid(column=1, row=5)
    except:
        print('No Transit file in directory')
        lbl3 = Label(window, text=f'use default hyperc_transit.', font=("Arial Bold", 12))
        lbl3.grid(column=1, row=5)
    lbl3 = Label(window, text=f'Start loading tables.', font=("Arial Bold", 12))
    lbl3.grid(column=1, row=6)

def prepare_calendar():
    #Make Calendar df
    import datetime
    lbl3 = Label(window, text="Prepare calendar", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=5)
    i = 0
    current_date_temp = datetime.datetime.strptime(start_date, "%d/%m/%y")
    new_date = current_date_temp + datetime.timedelta(days=7)
    global first_week_date
    global Calendar
    Calendar = pd.DataFrame({'WEEK_START_DATE' : [current_date_temp], 'NEXT_WEEK_START_DATE' : [new_date], 'WEEK_INDEX':[i+1], 'DAYS_FROM_NOW':[7*i], 'batches_qty':[0]})
    while i < weeks_number:
        current_date_temp = new_date
        new_date = current_date_temp + datetime.timedelta(days=7)
        i += 1
        Calendar = Calendar.append({'WEEK_START_DATE' : current_date_temp, 'NEXT_WEEK_START_DATE' : new_date, 'WEEK_INDEX' : i+1, 'DAYS_FROM_NOW' : 7*i, 'batches_qty' : 0}, ignore_index = True)

def load_calendar():
    #Refill calendar table
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
             ssh_username=REMOTE_USERNAME,
             ssh_pkey = r"./id_rsa",
             remote_bind_address=('localhost', PORT),
             local_bind_address=('localhost', PORT)):
         conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
         cur = conn.cursor()
         cur.execute('DELETE FROM "public"."calendar";')
         conn.commit()
         cur.close()
         conn.close()
    print("Table calendar cleaned")
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
             ssh_username=REMOTE_USERNAME,
             ssh_pkey = r"./id_rsa",
             remote_bind_address=('localhost', PORT),
             local_bind_address=('localhost', PORT)):
         conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
         execute_values(conn, Calendar.astype(str), 'calendar')
         conn.close()
    print("Table calendar refilled")
    lbl3 = Label(window, text="Calendar loaded", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=6)

def load_products():
    products_table['min_logistic_time'] = products_table['LEAD_TIME_WEEKS'] + min(logistic_costs['delivery_time'])
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
             ssh_username=REMOTE_USERNAME,
             ssh_pkey = r"./id_rsa",
             remote_bind_address=('localhost', PORT),
             local_bind_address=('localhost', PORT)):
         conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
         cur = conn.cursor()
         cur.execute('DELETE FROM "public"."products";')
         conn.commit()
         cur.close()
         conn.close()
    print("Table products cleaned")
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
             ssh_username=REMOTE_USERNAME,
             ssh_pkey = r"./id_rsa",
             remote_bind_address=('localhost', PORT),
             local_bind_address=('localhost', PORT)):
         conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
         execute_values(conn, products_table.astype(str), 'products')
         conn.close()
    print("Table products refilled")

    reindex = '''
    update products  
    set "INDEX" = index_t."Index"
    FROM (select 
    "ASIN",	  
    row_number () over() as "Index"
    from products) as index_t
    where products."ASIN" = index_t."ASIN";
    '''

    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
             ssh_username=REMOTE_USERNAME,
             ssh_pkey = r"./id_rsa",
             remote_bind_address=('localhost', PORT),
             local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute(reindex)
        conn.commit()
        cur.close()
        conn.close()
    print("Table products reindexed")
    lbl3 = Label(window, text="Products loaded", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=7)

def prepare_in_delivery():
    from datetime import date, timedelta
    global in_delivery
    in_delivery = Denorm_table[['ASIN', 'IN_DELIVERY_UNITS1', 'IN_DELIVERY_SUM1', 'IN_DELIVERY_ETA1']].dropna()
    in_delivery = in_delivery.rename(columns = {"IN_DELIVERY_UNITS1" : "QTY", "IN_DELIVERY_ETA1" : "IN_DELIVERY_ETA", "IN_DELIVERY_SUM1" : "sum"})
    in_d1 =  Denorm_table[['ASIN', 'IN_DELIVERY_UNITS2', 'IN_DELIVERY_SUM2', 'IN_DELIVERY_ETA2']].dropna()
    in_d1 = in_d1.rename(columns = {"IN_DELIVERY_UNITS2" : "QTY", "IN_DELIVERY_ETA2" : "IN_DELIVERY_ETA", "IN_DELIVERY_SUM2" : "sum"})
    in_d2 =  Denorm_table[['ASIN', 'IN_DELIVERY_UNITS3', 'IN_DELIVERY_SUM3', 'IN_DELIVERY_ETA3']].dropna()
    in_d2 = in_d2.rename(columns = {"IN_DELIVERY_UNITS3" : "QTY", "IN_DELIVERY_ETA3" : "IN_DELIVERY_ETA", "IN_DELIVERY_SUM3" : "sum"})
    in_delivery = pd.concat([in_delivery, in_d1, in_d2])
    in_delivery['QTY'] = in_delivery['QTY'].astype(int)
    in_delivery['sum'] = in_delivery['sum'].astype(float)
    in_delivery['IN_DELIVERY_ETA'] = pd.to_datetime(in_delivery['IN_DELIVERY_ETA'])
    in_delivery['IN_DELIVERY_ETA_WEEK_START_DATE'] = in_delivery['IN_DELIVERY_ETA'].dt.to_period('W').apply(lambda r: r.start_time)
    in_delivery = in_delivery.merge(Calendar[['WEEK_START_DATE', 'WEEK_INDEX']].rename(columns={"WEEK_START_DATE" : "IN_DELIVERY_ETA_WEEK_START_DATE", "WEEK_INDEX": "IN_DELIVERY_ETA_WEEK"}), how="left", on=['IN_DELIVERY_ETA_WEEK_START_DATE'])
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute('DELETE FROM "public"."in_delivery";')
        conn.commit()
        cur.close()
        conn.close()
    print("Table in_delivery cleaned")
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        execute_values(conn, in_delivery.astype(str), 'in_delivery')
        conn.close()
    print("Table in_delivery refilled")
    #ADD 50 '-' to in_delivery
    i=0
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        while i < 10:
            cur.execute('''
            insert into "public"."in_delivery" ("ASIN") values ('-');
            insert into "public"."in_delivery" ("ASIN") values ('-');
            insert into "public"."in_delivery" ("ASIN") values ('-');
            insert into "public"."in_delivery" ("ASIN") values ('-');
            insert into "public"."in_delivery" ("ASIN") values ('-');
            ''')
            i += 1
        conn.commit()
        cur.close()
        conn.close()
    print("Added 50 -")    
    lbl3 = Label(window, text="Table in_delivery loaded", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=8)

def prepare_consig_reports_random_buffer():
    i=0
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute('DELETE FROM "public"."consignments"; DELETE FROM "public"."order_buffer";')
        conn.commit()
        while i < 20:
            cur.execute('''
            insert into "public"."consignments" ("NAME") values ('-');
            insert into "public"."consignments" ("NAME") values ('-');
            insert into "public"."consignments" ("NAME") values ('-');
            insert into "public"."order_buffer" ("consignment") values ('-');
            insert into "public"."order_buffer" ("consignment") values ('-');
            insert into "public"."order_buffer" ("consignment") values ('-');
            ''')
            i += 1
        conn.commit()
        cur.close()
        conn.close()
    print("Added 60 blank consigments and buffers")
    #Refill roe table
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute('DELETE FROM "public"."report"; DELETE FROM "public"."report_export"; DELETE FROM "public"."random";')
        conn.commit()
        cur.close()
        conn.close()
    print("Report tables cleaned")
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute('''
        INSERT INTO "public"."report" ("ASIN", "PRODUCT", "PROD_INDEX") 
        (
        with _products_dict as (
            select distinct 
            p."ASIN",
            p."DESCRIPTION" as "PRODUCT",
            p."INDEX" as "PROD_INDEX"
            from products p)
        select 
        p."ASIN",
        p."PRODUCT",
        p."PROD_INDEX"
        from _products_dict as p);
        INSERT INTO "public"."report_export" ("ASIN", "PRODUCT", "PROD_INDEX") 
        (
        with _products_dict as (
            select distinct 
            p."ASIN",
            p."DESCRIPTION" as "PRODUCT",
            p."INDEX" as "PROD_INDEX"
            from products p)
        select 
        p."ASIN",
        p."PRODUCT",
        p."PROD_INDEX"
        from _products_dict as p);
        ''')
        conn.commit()
        cur.close()
        conn.close()
    print("Report tables refilled")
    lbl3 = Label(window, text="Report tables refilled", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=9)
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute(random_t)
        conn.commit()
        cur.close()
        conn.close()
    print("Random table refilled")

def update_roe():
    #Refill roe table
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute(f'''DELETE FROM "public"."roe"; DELETE FROM "public"."sys_dashboard"; INSERT INTO "public"."sys_dashboard" ("CURRENT_CALCULATED_WEEK") VALUES(1); update "public"."sys_dashboard" set "CURRENT_CALCULATED_DATE" = '{first_week_date}';''')
        conn.commit()
        cur.close()
        conn.close()
    print("Table roe cleaned")
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute('''
        INSERT INTO "public"."roe" ("ASIN", "INVENTORY", "inventory_sum") 
        (
        with _products_dict as (
            select distinct 
            p."ASIN"
            from products p),
            _inv_in_stocks as (
            select 
            inv."ASIN",
            inv."QTY_STOCK",
            inv."sum_stock"
            from inventory inv),
            _inv_in_delivery as (
            select 
            in_d."ASIN",
            sum(in_d."QTY") as "QTY",
            sum(in_d."sum") as "sum"
            from in_delivery in_d
            group by
            in_d."ASIN" )
        select 
        p."ASIN",
        COALESCE(invs."QTY_STOCK",0) + COALESCE(invd."QTY",0) as "INVENTORY",
        COALESCE(invs."sum_stock",0) + COALESCE(invd."sum",0) as "inventory_sum"
        from _products_dict as p
        left join _inv_in_stocks as invs on invs."ASIN" = p."ASIN" 
        left join _inv_in_delivery as invd on invd."ASIN" = p."ASIN" );
        Update roe set "PERIOD" = 4;
        Update roe set "CURRENT_PERIOD" = 1;
        Update roe set "ROE_BENCHMARK" = 0.05;
        ''')
        conn.commit()
        cur.close()
        conn.close()
    print("Table roe refilled")
    lbl3 = Label(window, text="Table roe refilled", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=9)

def prepare_inventory():
    global inventory
    inventory = Denorm_table[['ASIN', 'QTY_AMZ', 'SUM_AMZ']].dropna()
    inventory['WH_NAME'] = 'AMZ'
    inventory['QTY_AMZ'] = inventory['QTY_AMZ'].astype(int)
    inventory['SUM_AMZ'] = inventory['SUM_AMZ'].astype(float)
    inventory['aver_cost'] = (inventory['SUM_AMZ'] / inventory['QTY_AMZ']).replace(np.inf, 0).replace(np.nan, 0)
    inventory = inventory.rename(columns={"QTY_AMZ" : "QTY_STOCK", "SUM_AMZ" : "sum_stock"})
    #Refill inventory table
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute('DELETE FROM "public"."inventory";')
        conn.commit()
        cur.close()
        conn.close()
    print("Table inventory cleaned")
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        execute_values(conn, inventory.astype(str), 'inventory')
        conn.close()
    print("Table inventory refilled")
    lbl3 = Label(window, text="Table inventory refilled", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=10)

def prepare_sales():
    global sales
    global Denorm_table
    client_seasonality1 = Denorm_table[['ASIN', 'WEEKLY_SALES_1_2_M']].rename(columns={"WEEKLY_SALES_1_2_M" : "QTY"}).replace(np.nan,0)
    client_seasonality1['MONTH'] = 1
    client_seasonality2 = Denorm_table[['ASIN', 'WEEKLY_SALES_1_2_M']].rename(columns={"WEEKLY_SALES_1_2_M" : "QTY"}).replace(np.nan,0)
    client_seasonality2['MONTH'] = 2
    client_seasonality3 = Denorm_table[['ASIN', 'WEEKLY_SALES_3_4_M']].rename(columns={"WEEKLY_SALES_3_4_M" : "QTY"}).replace(np.nan,0)
    client_seasonality3['MONTH'] = 3
    client_seasonality4 = Denorm_table[['ASIN', 'WEEKLY_SALES_3_4_M']].rename(columns={"WEEKLY_SALES_3_4_M" : "QTY"}).replace(np.nan,0)
    client_seasonality4['MONTH'] = 4
    client_seasonality5 = Denorm_table[['ASIN', 'WEEKLY_SALES_5_6_M']].rename(columns={"WEEKLY_SALES_5_6_M" : "QTY"}).replace(np.nan,0)
    client_seasonality5['MONTH'] = 5
    client_seasonality6 = Denorm_table[['ASIN', 'WEEKLY_SALES_5_6_M']].rename(columns={"WEEKLY_SALES_5_6_M" : "QTY"}).replace(np.nan,0)
    client_seasonality6['MONTH'] = 6
    client_seasonality7 = Denorm_table[['ASIN', 'WEEKLY_SALES_7_8_M']].rename(columns={"WEEKLY_SALES_7_8_M" : "QTY"}).replace(np.nan,0)
    client_seasonality7['MONTH'] = 7
    client_seasonality8 = Denorm_table[['ASIN', 'WEEKLY_SALES_7_8_M']].rename(columns={"WEEKLY_SALES_7_8_M" : "QTY"}).replace(np.nan,0)
    client_seasonality8['MONTH'] = 8
    client_seasonality9 = Denorm_table[['ASIN', 'WEEKLY_SALES_9_10_M']].rename(columns={"WEEKLY_SALES_9_10_M" : "QTY"}).replace(np.nan,0)
    client_seasonality9['MONTH'] = 9
    client_seasonality10 = Denorm_table[['ASIN', 'WEEKLY_SALES_9_10_M']].rename(columns={"WEEKLY_SALES_9_10_M" : "QTY"}).replace(np.nan,0)
    client_seasonality10['MONTH'] = 10
    client_seasonality11 = Denorm_table[['ASIN', 'WEEKLY_SALES_11_12_M']].rename(columns={"WEEKLY_SALES_11_12_M" : "QTY"}).replace(np.nan,0)
    client_seasonality11['MONTH'] = 11
    client_seasonality12 = Denorm_table[['ASIN', 'WEEKLY_SALES_11_12_M']].rename(columns={"WEEKLY_SALES_11_12_M" : "QTY"}).replace(np.nan,0)
    client_seasonality12['MONTH'] = 12
    client_seasonality = pd.concat([client_seasonality1, client_seasonality2, client_seasonality3, client_seasonality4, client_seasonality5, client_seasonality6, client_seasonality7, client_seasonality8, client_seasonality9, client_seasonality10, client_seasonality11, client_seasonality12])
    pr = products_table
    pr['cross'] = 0
    cld = Calendar
    cld['cross'] = 0
    sales = pr[['ASIN', 'cross']].merge(cld[['WEEK_START_DATE', 'cross']], how="outer", on=['cross'])
    del sales['cross']
    sales['WEEK_START_DATE'] = pd.to_datetime(sales['WEEK_START_DATE'])
    sales['MONTH'] = pd.DatetimeIndex(sales['WEEK_START_DATE']).month.astype(int)
    sales = sales.merge(client_seasonality[['ASIN', 'MONTH', 'QTY']], how="left", on=['ASIN', 'MONTH'])
    sales['QTY'] = sales['QTY'].astype(int)
    del sales['MONTH']

    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute('DELETE FROM "public"."sales";')
        conn.commit()
        cur.close()
        conn.close()
    print("Table sales cleaned")
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        execute_values(conn, sales.astype(str), 'sales')
        conn.close()
    print("Table sales refilled")
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute('''
        update sales set "RECEIVING_SHPMNTS_COUNT" = temp."RECEIVING_SHPMNTS_COUNT"
            from 
            (select 
            count(id."QTY") as "RECEIVING_SHPMNTS_COUNT",
            id."IN_DELIVERY_ETA_WEEK_START_DATE",
            id."ASIN"
            from in_delivery as id
            where id."QTY" > 0
            group by 
            id."IN_DELIVERY_ETA_WEEK_START_DATE",
            id."ASIN") as temp
            where temp."IN_DELIVERY_ETA_WEEK_START_DATE" = sales."WEEK_START_DATE" and temp."ASIN" = sales."ASIN" ;
        ''')
        conn.commit()
        cur.close()
        conn.close()
    print("Table sales in_delivery counts updated")
    lbl3 = Label(window, text="Table sales refilled, updating box_templates...", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=11)

def prepare_box_templates():
    global box_template
    box_template1 = Denorm_table[['ASIN', 'UNITS_PER_BOX1', 'BOX1_H', 'BOX1_W', 'BOX1_L', 'BOX1_WEIGHT', 'BOXES_PER_PALLET1']].rename(columns={"UNITS_PER_BOX1" : "UNITS_PER_BOX", "BOX1_H" : "BOX_H", "BOX1_W" : "BOX_W", "BOX1_L" : "BOX_L", "BOX1_WEIGHT" : "BOX_WEIGHT", "BOXES_PER_PALLET1" : "BOXES_PER_PALLET"}).replace(np.nan,0)
    try : box_template2 = Denorm_table[['ASIN', 'UNITS_PER_BOX2', 'BOX2_H', 'BOX2_W', 'BOX2_L', 'BOX2_WEIGHT', 'BOXES_PER_PALLET2']].rename(columns={"UNITS_PER_BOX2" : "UNITS_PER_BOX", "BOX2_H" : "BOX_H", "BOX2_W" : "BOX_W", "BOX2_L" : "BOX_L", "BOX2_WEIGHT" : "BOX_WEIGHT", "BOXES_PER_PALLET2" : "BOXES_PER_PALLET"}).replace(np.nan,0)
    except :    
        print('No BOX2, skip')
        box_template2 = pd.DataFrame(columns={'ASIN', 'UNITS_PER_BOX', 'BOX_H', 'BOX_W', 'BOX_L', 'BOX_WEIGHT', 'BOXES_PER_PALLET'})
    try : box_template3 = Denorm_table[['ASIN', 'UNITS_PER_BOX3', 'BOX3_H', 'BOX3_W', 'BOX3_L', 'BOX3_WEIGHT', 'BOXES_PER_PALLET3']].rename(columns={"UNITS_PER_BOX3" : "UNITS_PER_BOX", "BOX3_H" : "BOX_H", "BOX3_W" : "BOX_W", "BOX3_L" : "BOX_L", "BOX3_WEIGHT" : "BOX_WEIGHT", "BOXES_PER_PALLET3" : "BOXES_PER_PALLET"}).replace(np.nan,0)
    except : 
        print('No BOX3, skip')
        box_template3 = pd.DataFrame(columns={'ASIN', 'UNITS_PER_BOX', 'BOX_H', 'BOX_W', 'BOX_L', 'BOX_WEIGHT', 'BOXES_PER_PALLET'})
    box_template = pd.concat([box_template1, box_template2, box_template3])
    box_template['BOX_TEMPLATE'] = box_template['BOX_H'].astype(str) + 'x' + box_template['BOX_W'].astype(str) + 'x' + box_template['BOX_L'].astype(str)
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        cur = conn.cursor()
        cur.execute('''DELETE FROM "public"."box_templates"; ''')
        conn.commit()
        cur.close()
        conn.close()
    print("Table box_templates cleaned")
    with SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
            ssh_username=REMOTE_USERNAME,
            ssh_pkey = r"./id_rsa",
            remote_bind_address=('localhost', PORT),
            local_bind_address=('localhost', PORT)):
        conn = psycopg2.connect(dbname = DATABASE, user = USER, password='', host='localhost', port=PORT)
        execute_values(conn, box_template.astype(str), 'box_templates')
        conn.close()
    print("Table box_templates refilled")
    lbl3 = Label(window, text="Table box_templates refilled, saving files...", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=12)

def save():
    box_template.to_excel(r"box_templates.xlsx", index=False)
    sales.to_excel(r"sales.xlsx", index=False)
    Calendar.to_excel(r"calendar.xlsx", index=False)
    products_table.to_excel(r"products.xlsx", index=False)
    in_delivery.to_excel(r"in_delivery.xlsx", index=False)
    inventory.to_excel(r"inventory.xlsx", index=False)
    lbl3 = Label(window, text="Saved files", font=("Arial Bold", 12))
    lbl3.grid(column=0, row=13)


window = Tk()
window.title("Loader v 0.1")
window.geometry('800x400')
lbl = Label(window, text="Name of DataBase", font=("Arial Bold", 12))
lbl.grid(column=0, row=0)

database = Entry(window, width=20)
database.grid(column=1, row=0)
database.focus()

lbl2 = Label(window, text="User", font=("Arial Bold", 12))
lbl2.grid(column=0, row=1)

usernameform = Entry(window, width=20)
usernameform.grid(column=1, row=1)

lbl3 = Label(window, text="Port", font=("Arial Bold", 12))
lbl3.grid(column=0, row=2)

portform = Entry(window, width=20)
portform.grid(column=1, row=2)

Btn = Button(window, text="Create_new_DB", command=clicked_new)
Btn.grid(column=1, row=3)

Btn = Button(window, text="Refill_existing_DB", command=clicked_refill)
Btn.grid(column=3, row=3)

window.mainloop()