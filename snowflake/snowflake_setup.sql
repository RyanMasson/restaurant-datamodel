-- Author: Ryan Masson
-- Part of: Restaurant Data Model project

-- Running this SQL file in Snowflake creates a warehouse, two databases, a schema, and a stage.

CREATE WAREHOUSE IF NOT EXISTS transforming;
CREATE DATABASE IF NOT EXISTS raw;  -- database for raw data
CREATE DATABASE IF NOT EXISTS analytics; -- database for future dbt development
CREATE SCHEMA IF NOT EXISTS raw.restaurant;

-- create a file format for the CSVs
CREATE OR REPLACE FILE FORMAT raw.restaurant.csv_format
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('')
    EMPTY_FIELD_AS_NULL = TRUE;

-- create a stage object for the raw database
CREATE OR REPLACE STAGE raw.restaurant.csv_stage
    FILE_FORMAT = raw.restaurant.csv_format;

-- MANUAL STEP: upload mock data CSVs into the stage via the Snowsight web app

-- ---------------------------------------------------------
-- Master Product List
-- Source: master_product_list.csv
-- Grain: one row per product
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw.restaurant.master_product_list (
    category VARCHAR,
    subcategory VARCHAR,
    primary_key VARCHAR,
    item_name VARCHAR,
    unit_of_measure VARCHAR,
    wholesale_price NUMBER(10,2),
    primary_vendor VARCHAR,
    secondary_vendor VARCHAR,
    buy_method VARCHAR,
    description VARCHAR
);

COPY INTO raw.restaurant.master_product_list
FROM @raw.restaurant.csv_stage/master_product_list.csv
FILE_FORMAT = (FORMAT_NAME = raw.restaurant.csv_format)
ON_ERROR = 'ABORT_STATEMENT';

-- ---------------------------------------------------------
-- Menu Item Snapshots
-- Source: menu_item_snapshots.csv
-- Grain: one row per menu item per monthly extract
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw.restaurant.menu_item_snapshots (
    extract_date DATE,
    business_key VARCHAR,
    pos_code VARCHAR,
    menu_item_name VARCHAR,
    category VARCHAR,
    subcategory VARCHAR,
    price NUMBER(10,2),
    description VARCHAR,
    is_active BOOLEAN,
    is_vegetarian BOOLEAN,
    is_vegan BOOLEAN,
    is_gluten_free BOOLEAN
);

COPY INTO raw.restaurant.menu_item_snapshots
FROM @raw.restaurant.csv_stage/menu_item_snapshots.csv
FILE_FORMAT = (FORMAT_NAME = raw.restaurant.csv_format)
ON_ERROR = 'ABORT_STATEMENT';

-- ---------------------------------------------------------
-- Purchase Order Headers
-- Source: purchase_order_headers.csv
-- Grain: one row per purchase order
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw.restaurant.purchase_order_headers (
    po_number VARCHAR,
    order_date DATE,
    vendor VARCHAR,
    employee_id VARCHAR,
    employee_name VARCHAR,
    employee_role VARCHAR,
    store_id VARCHAR,
    store_name VARCHAR,
    buy_method VARCHAR 
);

COPY INTO raw.restaurant.purchase_order_headers
FROM @raw.restaurant.csv_stage/purchase_order_headers.csv
FILE_FORMAT = (FORMAT_NAME = raw.restaurant.csv_format)
ON_ERROR = 'ABORT_STATEMENT';

-- ---------------------------------------------------------
-- Purchase Order Lines
-- Source: purchase_order_lines.csv
-- Grain: one row per line item per purchase order made to a vendor
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw.restaurant.purchase_order_lines (
    po_number VARCHAR,
    line_number NUMBER,
    product_primary_key VARCHAR,
    item_name VARCHAR,
    category VARCHAR,
    subcategory VARCHAR,
    unit_of_measure VARCHAR,
    quantity_ordered NUMBER(10,2),
    unit_price NUMBER(10,2),
    extended_price NUMBER(10,2),
    discount_amount NUMBER(10,2),
    net_purchase_amount NUMBER(10,2)
);

COPY INTO raw.restaurant.purchase_order_lines
FROM @raw.restaurant.csv_stage/purchase_order_lines.csv
FILE_FORMAT = (FORMAT_NAME = raw.restaurant.csv_format)
ON_ERROR = 'ABORT_STATEMENT';

-- ---------------------------------------------------------
-- Inventory Valuation Headers
-- Source: inventory_valuation_headers.csv
-- Grain: one row per monthly inventory valuation
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw.restaurant.inventory_valuation_headers (
    valuation_id VARCHAR,
    inventory_date DATE,
    store_id VARCHAR,
    store_name VARCHAR,
    counted_by VARCHAR,
    extended_by VARCHAR
);

COPY INTO raw.restaurant.inventory_valuation_headers
FROM @raw.restaurant.csv_stage/inventory_valuation_headers.csv
FILE_FORMAT = (FORMAT_NAME = raw.restaurant.csv_format)
ON_ERROR = 'ABORT_STATEMENT';

-- ---------------------------------------------------------
-- Inventory Valuation Lines
-- Source: inventory_valuation_lines.csv
-- Grain: one row per product per monthly inventory valuation
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw.restaurant.inventory_valuation_lines (
    valuation_id VARCHAR,
    item VARCHAR,
    item_primary_key VARCHAR,
    category VARCHAR,
    subcategory VARCHAR,
    unit VARCHAR,
    item_amount NUMBER(10,2),
    item_unit_value NUMBER(10,2),
    inventory_value NUMBER(10,2)
);

COPY INTO raw.restaurant.inventory_valuation_lines
FROM @raw.restaurant.csv_stage/inventory_valuation_lines.csv
FILE_FORMAT = (FORMAT_NAME = raw.restaurant.csv_format)
ON_ERROR = 'ABORT_STATEMENT';

-- ---------------------------------------------------------
-- Sales Order Headers
-- Source: sales_order_headers.csv
-- Grain: one row per order ticket
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw.restaurant.sales_order_headers (
    order_ticket_number VARCHAR,
    order_timestamp TIMESTAMP_NTZ,
    employee_id VARCHAR,
    employee_name VARCHAR,
    store_id VARCHAR,
    store_name VARCHAR,
    order_channel VARCHAR
);

COPY INTO raw.restaurant.sales_order_headers
FROM @raw.restaurant.csv_stage/sales_order_headers.csv
FILE_FORMAT = (FORMAT_NAME = raw.restaurant.csv_format)
ON_ERROR = 'ABORT_STATEMENT';

-- ---------------------------------------------------------
-- Sales Order Lines
-- Source: sales_order_lines.csv
-- Grain: one row per menu item per order ticket
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw.restaurant.sales_order_lines (
    order_ticket_number   VARCHAR,
    line_number           NUMBER,
    menu_item_pos_code    VARCHAR,
    menu_item_name        VARCHAR,
    category              VARCHAR,
    subcategory           VARCHAR,
    quantity_sold         NUMBER(10,2),
    unit_price            NUMBER(10,2),
    extended_price        NUMBER(10,2),
    discount_amount       NUMBER(10,2),
    net_sales_amount      NUMBER(10,2)
);

COPY INTO raw.restaurant.sales_order_lines
FROM @raw.restaurant.csv_stage/sales_order_lines.csv
FILE_FORMAT = (FORMAT_NAME = raw.restaurant.csv_format)
ON_ERROR = 'ABORT_STATEMENT';