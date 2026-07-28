create warehouse transforming;
create database raw;  -- database for raw data
create database analytics; -- database for future dbt development
create schema raw.restaurant;


USE DATABASE raw;
USE SCHEMA restaurant;

-- ---------------------------------------------------------
-- Master Product List
-- Source: master_product_list.csv
-- Grain: one row per product
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw_master_product_list (
    category            VARCHAR      COMMENT 'Non-Alcoholic Beverage, Alcoholic Beverage, Dry Goods & Spices, Frozen/Refrigerated Goods, Liquids/Pastes/Sauces, Produce & Meat, Supplies',
    subcategory         VARCHAR,
    primary_key         VARCHAR      COMMENT 'Natural/business key, e.g. NAB-001',
    item_name           VARCHAR,
    unit_of_measure     VARCHAR,
    wholesale_price     NUMBER(10,2),
    primary_vendor      VARCHAR,
    secondary_vendor    VARCHAR,
    buy_method          VARCHAR      COMMENT 'Vendor App, Text Message, Website',
    description         VARCHAR
)
COMMENT = 'Raw landing table for the restaurant master product list';

-- ---------------------------------------------------------
-- Menu Item Snapshots
-- Source: menu_item_snapshots.csv
-- Grain: one row per menu item per monthly extract
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw_menu_item_snapshots (
    extract_date        DATE         COMMENT 'Point-in-time snapshot date, not SCD effective/expiration',
    business_key         VARCHAR,
    pos_code             VARCHAR,
    menu_item_name       VARCHAR,
    category             VARCHAR      COMMENT 'Food, Beverage',
    subcategory          VARCHAR      COMMENT 'Appetizer, Entree, Side, Non-Alcoholic, Alcoholic',
    price                NUMBER(10,2),
    description           VARCHAR,
    is_active             BOOLEAN,
    is_vegetarian         BOOLEAN,
    is_vegan              BOOLEAN,
    is_gluten_free        BOOLEAN
)
COMMENT = 'Raw landing table for monthly menu item export snapshots; SCD Type 2 versioning is derived downstream in dbt';

-- ---------------------------------------------------------
-- Purchase Order Headers
-- Source: purchase_order_headers.csv
-- Grain: one row per purchase order
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw_purchase_order_headers (
    po_number            VARCHAR      COMMENT 'Degenerate dimension',
    order_date            DATE,
    vendor                VARCHAR,
    employee_id           VARCHAR,
    employee_name         VARCHAR,
    employee_role         VARCHAR,
    store_id              VARCHAR,
    store_name            VARCHAR,
    buy_method            VARCHAR      COMMENT 'Vendor App, Text Message, Website'
)
COMMENT = 'Raw landing table for vendor purchase order headers';

-- ---------------------------------------------------------
-- Purchase Order Lines
-- Source: purchase_order_lines.csv
-- Grain: one row per line item per purchase order made to a vendor
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw_purchase_order_lines (
    po_number             VARCHAR      COMMENT 'Joins to raw_purchase_order_headers.po_number',
    line_number           NUMBER,
    product_primary_key   VARCHAR      COMMENT 'Joins to raw_master_product_list.primary_key',
    item_name             VARCHAR,
    category              VARCHAR,
    subcategory           VARCHAR,
    unit_of_measure       VARCHAR,
    quantity_ordered      NUMBER(10,2) COMMENT 'Additive fact',
    unit_price            NUMBER(10,2) COMMENT 'Non-additive fact',
    extended_price        NUMBER(10,2) COMMENT 'Additive fact',
    discount_amount       NUMBER(10,2) COMMENT 'Additive fact',
    net_purchase_amount   NUMBER(10,2) COMMENT 'Additive fact'
)
COMMENT = 'Raw landing table for vendor purchase order line items';

-- ---------------------------------------------------------
-- Inventory Valuation Headers
-- Source: inventory_valuation_headers.csv
-- Grain: one row per monthly inventory valuation
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw_inventory_valuation_headers (
    valuation_id          VARCHAR,
    inventory_date        DATE,
    store_id              VARCHAR,
    store_name            VARCHAR,
    counted_by            VARCHAR,
    extended_by           VARCHAR
)
COMMENT = 'Raw landing table for monthly inventory valuation headers';

-- ---------------------------------------------------------
-- Inventory Valuation Lines
-- Source: inventory_valuation_lines.csv
-- Grain: one row per product per monthly inventory valuation
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw_inventory_valuation_lines (
    valuation_id          VARCHAR      COMMENT 'Joins to raw_inventory_valuation_headers.valuation_id',
    item                  VARCHAR,
    item_primary_key      VARCHAR      COMMENT 'Joins to raw_master_product_list.primary_key',
    category              VARCHAR,
    subcategory           VARCHAR,
    unit                  VARCHAR,
    item_amount           NUMBER(10,2) COMMENT 'Semi-additive fact — snapshot quantity on hand',
    item_unit_value       NUMBER(10,2) COMMENT 'Non-additive fact',
    inventory_value       NUMBER(10,2) COMMENT 'Semi-additive fact — item_amount x item_unit_value'
)
COMMENT = 'Raw landing table for monthly inventory valuation line items';

-- ---------------------------------------------------------
-- Sales Order Headers
-- Source: sales_order_headers.csv
-- Grain: one row per order ticket
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw_sales_order_headers (
    order_ticket_number   VARCHAR      COMMENT 'Degenerate dimension',
    order_timestamp       TIMESTAMP_NTZ COMMENT 'Raw datetime; date/time-of-day split happens downstream in dbt',
    employee_id           VARCHAR,
    employee_name         VARCHAR,
    store_id              VARCHAR,
    store_name            VARCHAR,
    order_channel         VARCHAR      COMMENT 'Raw string, e.g. Dine In, Takeout, DoorDash, Uber Eats, Grubhub'
)
COMMENT = 'Raw landing table for POS sales order headers';

-- ---------------------------------------------------------
-- Sales Order Lines
-- Source: sales_order_lines.csv
-- Grain: one row per menu item per order ticket
-- ---------------------------------------------------------
CREATE OR REPLACE TABLE raw_sales_order_lines (
    order_ticket_number   VARCHAR      COMMENT 'Joins to raw_sales_order_headers.order_ticket_number',
    line_number           NUMBER,
    menu_item_pos_code    VARCHAR      COMMENT 'Joins to raw_menu_item_snapshots.pos_code',
    menu_item_name        VARCHAR,
    category              VARCHAR,
    subcategory           VARCHAR,
    quantity_sold         NUMBER(10,2) COMMENT 'Additive fact',
    unit_price            NUMBER(10,2) COMMENT 'Non-additive fact',
    extended_price        NUMBER(10,2) COMMENT 'Additive fact',
    discount_amount       NUMBER(10,2) COMMENT 'Additive fact',
    net_sales_amount      NUMBER(10,2) COMMENT 'Additive fact'
)
COMMENT = 'Raw landing table for POS sales order line items';