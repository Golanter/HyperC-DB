DROP TABLE IF EXISTS "public"."box_templates";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."box_templates" (
    "BOX_TEMPLATE" text NOT NULL DEFAULT '-'::text,
    "ASIN" text NOT NULL DEFAULT '-'::text,
    "UNITS_PER_BOX" int8 NOT NULL DEFAULT 0,
    "BOX_H" float8 NOT NULL DEFAULT 0,
    "BOX_W" float8 NOT NULL DEFAULT 0,
    "BOX_L" float8 NOT NULL DEFAULT 0,
    "BOX_WEIGHT" float8 NOT NULL DEFAULT 0,
    "BOXES_PER_PALLET" float8 NOT NULL DEFAULT 0,
    "idx" int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
    PRIMARY KEY ("idx")
);

DROP TABLE IF EXISTS "public"."calendar";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."calendar" (
    "WEEK_START_DATE" text,
    "NEXT_WEEK_START_DATE" text,
    "WEEK_INDEX" int8 NOT NULL,
    "DAYS_FROM_NOW" int8 NOT NULL DEFAULT 0,
    "batches_qty" int8 NOT NULL DEFAULT 0,
    "idx" int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
    PRIMARY KEY ("WEEK_INDEX")
);

DROP TABLE IF EXISTS "public"."consignments";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."consignments" (
    "NAME" text NOT NULL DEFAULT '-'::text,
    "COST_PER_KG" float8 NOT NULL DEFAULT 0,
    "COST_PER_UNIT" float8 NOT NULL DEFAULT 0,
    "way_of_delivering" text NOT NULL DEFAULT '-'::text,
    "company" text NOT NULL DEFAULT '-'::text,
    "total_cost" float8 NOT NULL DEFAULT 0,
    "idx" int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
    "total_weight" float8 NOT NULL DEFAULT 0,
    "total_volume" float8 NOT NULL DEFAULT 0,
    "delivery_code" text NOT NULL DEFAULT '-'::text
);

DROP TABLE IF EXISTS "public"."in_delivery";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."in_delivery" (
    "ASIN" text NOT NULL DEFAULT '-'::text,
    "IN_DELIVERY_ETA" text NOT NULL DEFAULT '-'::text,
    "QTY" int8 NOT NULL DEFAULT 0,
    "SENDER" text NOT NULL DEFAULT '-'::text,
    "RECEIVER" text NOT NULL DEFAULT '-'::text,
    "PLAN_OR_FACT" text NOT NULL DEFAULT '-'::text,
    "IN_DELIVERY_SENT" text NOT NULL DEFAULT '-'::text,
    "IN_DELIVERY_ETA_WEEK" int8 NOT NULL DEFAULT 0,
    "IN_DELIVERY_SENT_WEEK" int8 NOT NULL DEFAULT 0,
    "COUNTED" text NOT NULL DEFAULT 'no'::text,
    "STATUS" text NOT NULL DEFAULT '-'::text,
    "IN_DELIVERY_ETA_WEEK_START_DATE" text NOT NULL DEFAULT '-'::text,
    "idx" int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
    "BOX_TEMPLATE" text NOT NULL DEFAULT '-'::text,
    "QTY_IN_SINGLE_BOX" int8 NOT NULL DEFAULT 0,
    "BOXES_QTY" int8 NOT NULL DEFAULT 0,
    "consig" text NOT NULL DEFAULT '-'::text,
    "delivery_code" text NOT NULL DEFAULT '-'::text,
    "sum" float8 NOT NULL DEFAULT 0,
    "weight" float8 NOT NULL DEFAULT 0,
    PRIMARY KEY ("idx")
);

DROP TABLE IF EXISTS "public"."inventory";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."inventory" (
    "ASIN" text NOT NULL,
    "QTY_STOCK" int8 DEFAULT 0,
    "WH_NAME" text,
    "sum_stock" float8 NOT NULL DEFAULT 0,
    "aver_cost" float8 NOT NULL DEFAULT 0,
    PRIMARY KEY ("ASIN")
);

DROP TABLE IF EXISTS "public"."logistic_costs";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."logistic_costs" (
    "company" text NOT NULL DEFAULT '-'::text,
    "way_of_delivering" text NOT NULL DEFAULT '-'::text,
    "kg_price" float8 NOT NULL DEFAULT 0,
    "value_weight" float8 NOT NULL DEFAULT 0,
    "batch_registration_price" float8 NOT NULL DEFAULT 0,
    "min_volume" float8 NOT NULL DEFAULT 0,
    "max_volume" float8 NOT NULL DEFAULT 0,
    "max_weight" float8 NOT NULL DEFAULT 0,
    "kg_cost_benchmark" float8 NOT NULL DEFAULT 0,
    "idx" int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
    "delivery_time" int8 NOT NULL DEFAULT 0,
    "delivery_code" text NOT NULL DEFAULT '-'::text,
    "min_weight" float8 NOT NULL DEFAULT 0,
    PRIMARY KEY ("idx")
);

DROP TABLE IF EXISTS "public"."order_buffer";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."order_buffer" (
    "TOTAL_VOLUME" float8 NOT NULL DEFAULT 0,
    "TOTAL_WEIGHT" float8 NOT NULL DEFAULT 0,
    "TOTAL_COST" float8 NOT NULL DEFAULT 0,
    "SUPPLIER" text NOT NULL DEFAULT '-'::text,
    "TOTAL_QTY" float8 NOT NULL DEFAULT 0,
    "DELIVERY_COST" float8 NOT NULL DEFAULT 0,
    "consignment" text NOT NULL DEFAULT '-'::text,
    "idx" int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
    "delivery_code" text NOT NULL DEFAULT '-'::text,
    "SENT_WEEK_DATE" text NOT NULL DEFAULT '-'::text,
    "ETA_WEEK_DATE" text NOT NULL DEFAULT '-'::text,
    "counted" text NOT NULL DEFAULT 'no'::text,
	PRIMARY KEY ("idx")
);

DROP TABLE IF EXISTS "public"."products";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."products" (
    "ASIN" text NOT NULL DEFAULT '-'::text,
    "SKU" text NOT NULL DEFAULT ' '::text,
    "DESCRIPTION" text NOT NULL DEFAULT '-'::text,
    "PRODUCT_CATEGORY_NAME" text NOT NULL DEFAULT ' '::text,
    "STATUS" text NOT NULL DEFAULT ' '::text,
    "INNERBOX_H" numeric NOT NULL DEFAULT 0,
    "INNERBOX_W" numeric NOT NULL DEFAULT 0,
    "INNERBOX_L" numeric NOT NULL DEFAULT 0,
    "UNIT_WEIGHT" numeric NOT NULL DEFAULT 0,
    "INDEX" int8 NOT NULL DEFAULT 0,
    "MINIMUM_SAFETY_QTY" int8 NOT NULL DEFAULT 0,
    "LEAD_TIME" int8 NOT NULL DEFAULT 7,
    "LEAD_TIME_WEEKS" int8 NOT NULL DEFAULT 1,
    "MOQ" int8 NOT NULL DEFAULT 50,
    "MARKUP" float8 NOT NULL DEFAULT 0.3,
    "min_logistic_time" int8 NOT NULL DEFAULT 2,
    "recom_retail_price" float8 NOT NULL DEFAULT 0,
    "purchase_price" float8 NOT NULL DEFAULT 0,
	"order_per_x_weeks" int8 NOT NULL DEFAULT 3,
	"unit_storage_cost" float8 NOT NULL DEFAULT 0.2,
    PRIMARY KEY ("ASIN")
);

DROP TABLE IF EXISTS "public"."random";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."random" (
    "qty" int4 NOT NULL DEFAULT 0,
    "s" text NOT NULL DEFAULT '-'::text,
    PRIMARY KEY ("qty")
);

DROP TABLE IF EXISTS "public"."report";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."report" (
    "WEEK_NUMBER" int8 NOT NULL DEFAULT 0,
    "WEEK_START_DATE" text NOT NULL DEFAULT '-'::text,
    "ASIN" text NOT NULL DEFAULT '-'::text,
    "PRODUCT" text NOT NULL DEFAULT '-'::text,
    "SELL_PLAN" int8 NOT NULL DEFAULT 0,
    "STOCK_IN_AMZ_END" int8 NOT NULL DEFAULT 0,
    "PLACE_ORDER" int8 NOT NULL DEFAULT 0,
    "SEND_TO_AMZ" int8 NOT NULL DEFAULT 0,
    "PROD_INDEX" int8 NOT NULL DEFAULT 0,
    "LOST_SALES" int8 NOT NULL DEFAULT 0,
    "STOCK_IN_AMZ_BEGIN" int8 NOT NULL DEFAULT 0,
    "QTY_ARRIVED_TO_AMZ" int8 NOT NULL DEFAULT 0,
    "PLAN_OR_FACT_ARRIVING" text NOT NULL DEFAULT '-'::text,
    "ROE" float8 NOT NULL DEFAULT 0,
    "INVENTORY_UNITS" float8 NOT NULL DEFAULT 0,
    "roe_period" float8 NOT NULL DEFAULT 0,
    "revenue" float8 NOT NULL DEFAULT 0,
    "profit" float8 NOT NULL DEFAULT 0,
    "STOCK_IN_AMZ_BEGIN_SUM" float8 NOT NULL DEFAULT 0,
    "STOCK_IN_AMZ_END_SUM" float8 NOT NULL DEFAULT 0,
    "LOST_REVENUE" float8 NOT NULL DEFAULT 0,
	"aver_cost_income_batch" float8 NOT NULL DEFAULT 0,
	"inv_sum" float8 NOT NULL DEFAULT 0,
	"order_counter" int8 NOT NULL DEFAULT 3,
	"storage_upcost" float8 NOT NULL DEFAULT 0,
	"cum_sum_inv_units" int8 NOT NULL DEFAULT 0,
    PRIMARY KEY ("ASIN")
);

DROP TABLE IF EXISTS "public"."report_export";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."report_export" (
    "WEEK_NUMBER" int8 NOT NULL DEFAULT 0,
    "WEEK_START_DATE" text NOT NULL DEFAULT '-'::text,
    "ASIN" text NOT NULL DEFAULT '-'::text,
    "PRODUCT" text NOT NULL DEFAULT '-'::text,
    "SELL_PLAN" int8 NOT NULL DEFAULT 0,
    "STOCK_IN_AMZ_END" int8 NOT NULL DEFAULT 0,
    "PLACE_ORDER" int8 NOT NULL DEFAULT 0,
    "SEND_TO_AMZ" int8 NOT NULL DEFAULT 0,
    "PROD_INDEX" int8 NOT NULL DEFAULT 0,
    "LOST_SALES" int8 NOT NULL DEFAULT 0,
    "STOCK_IN_AMZ_BEGIN" int8 NOT NULL DEFAULT 0,
    "QTY_ARRIVED_TO_AMZ" int8 NOT NULL DEFAULT 0,
    "PLAN_OR_FACT_ARRIVING" text NOT NULL DEFAULT '-'::text,
    "ROE" float8 NOT NULL DEFAULT 0,
    "INVENTORY_UNITS" float8 NOT NULL DEFAULT 0,
    "roe_period" float8 NOT NULL DEFAULT 0,
    "revenue" float8 NOT NULL DEFAULT 0,
    "profit" float8 NOT NULL DEFAULT 0,
    "STOCK_IN_AMZ_BEGIN_SUM" float8 NOT NULL DEFAULT 0,
    "STOCK_IN_AMZ_END_SUM" float8 NOT NULL DEFAULT 0,
    "LOST_REVENUE" float8 NOT NULL DEFAULT 0,
    "margin" float8 NOT NULL DEFAULT 0,
	"aver_cost_income_batch" float8 NOT NULL DEFAULT 0,
	"inv_sum" float8 NOT NULL DEFAULT 0,
	"storage_upcost" float8 NOT NULL DEFAULT 0,
    PRIMARY KEY ("ASIN")
);

DROP TABLE IF EXISTS "public"."roe";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."roe" (
    "ASIN" text DEFAULT '-'::text,
    "INVENTORY" float8 DEFAULT 0,
    "SALES" float8 DEFAULT 0,
    "ROE" float8 DEFAULT 0,
    "PERIOD" int4 NOT NULL DEFAULT 4,
    "CURRENT_PERIOD" int8 NOT NULL DEFAULT 1,
    "ROE_BENCHMARK" float8 NOT NULL DEFAULT 0.1,
    "roe_week" float8 NOT NULL DEFAULT 0,
    "aver_inv" float8 NOT NULL DEFAULT 0,
    "roe_period" float8 NOT NULL DEFAULT 0,
    "inventory_sum" float8 NOT NULL DEFAULT 0,
    "aver_inv_sum" float8 NOT NULL DEFAULT 0,
    "profit_period" float8 NOT NULL DEFAULT 0,
	"roe_consider" text DEFAULT 'no'::text,
	"order_counter" int8 NOT NULL DEFAULT 3,
	"CURRENT_PERIOD_storage" int8 NOT NULL DEFAULT 1,
	"PERIOD_storage" int8 NOT NULL DEFAULT 4,
    PRIMARY KEY ("ASIN")
);

DROP TABLE IF EXISTS "public"."sales";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."sales" (
    "ASIN" text NOT NULL DEFAULT '-'::text,
    "QTY" int8 NOT NULL DEFAULT 0,
    "WEEK_START_DATE" text NOT NULL DEFAULT '-'::text,
    "FROM_WH" text NOT NULL DEFAULT '-'::text,
    "RECEIVING_SHPMNTS_COUNT" int8 NOT NULL DEFAULT 0,
    "idx" int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
    "revenue" float8 NOT NULL DEFAULT 0,
    "profit" float8 NOT NULL DEFAULT 0,
    PRIMARY KEY ("idx")
);

DROP TABLE IF EXISTS "public"."suppliers";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."suppliers" (
    "SUPPLIER_NAME" text NOT NULL,
    "SKU" _varchar NOT NULL,
    "MOQ" int4 NOT NULL,
    "LEAD_TIME" int4 NOT NULL,
    "ADD_PRICE_UNIT" numeric,
    "idx" int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
    PRIMARY KEY ("idx")
);

DROP TABLE IF EXISTS "public"."sys_dashboard";
-- This script only contains the table creation statements and does not fully represent the table in database. It's still missing: indices, triggers. Do not use it as backup.

-- Table Definition
CREATE TABLE "public"."sys_dashboard" (
    "id" text NOT NULL DEFAULT '-'::text,
    "CURRENT_CALCULATED_DATE" text NOT NULL DEFAULT '2022-04-04'::text,
    "FC_LIMIT" int8 NOT NULL DEFAULT 5000,
	"SHIPMENTS_COUNT" int8 NOT NULL DEFAULT 0,
    "CURRENT_CALCULATED_WEEK" int8 NOT NULL DEFAULT 1,
    "PLANNING_FINISHED" bool DEFAULT true,
    "SAFETY_LIMIT" int8 DEFAULT 500,
    "SHIPMENTS_CALCULATED" int8 DEFAULT 1,
    "CURRENT_SOLD_ITEM" int8 DEFAULT 1,
    "ITEMS_COUNT" int8 NOT NULL DEFAULT 1,
    "ITEMS_IN_FC" int8 NOT NULL DEFAULT 4000,
    "LEAD_TIME" int4 DEFAULT 2,
    "EXPECT_ARRIVING" int8 NOT NULL DEFAULT 0,
    "STEP" int8 NOT NULL DEFAULT 0,
    "splited_proc" text NOT NULL DEFAULT '-'::text,
    "ORDER_BUFFER_CHECKED" bool NOT NULL DEFAULT true,
    "current_delivery_number" int8 NOT NULL DEFAULT 0,
    "order_index" int8 NOT NULL DEFAULT 0,
    "delivery_code" text NOT NULL DEFAULT '-'::text,
    "box_template" text NOT NULL DEFAULT '-'::text,
    "initiated" text NOT NULL DEFAULT 'no'::text,
    "roe_calculated_items" int8 NOT NULL DEFAULT 0,
	"delivery_count" int8 NOT NULL DEFAULT 0,
	"delivery_counted" int8 NOT NULL DEFAULT 0,
    PRIMARY KEY ("CURRENT_CALCULATED_WEEK")
);

