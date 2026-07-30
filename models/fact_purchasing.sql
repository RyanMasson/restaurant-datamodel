-- fact_purchasing: grain is one row per line item per purchase order
-- made to a vendor.
--
-- NOTE: Time of day is listed against Purchasing in the bus matrix,
-- but the mock purchase order data only has a date (Order Date), not
-- a timestamp — there's no time-of-day information to resolve for
-- this process. That FK is intentionally left out here rather than
-- joined against a meaningless default. Worth calling out as a known
-- gap between the declared bus matrix and the mock data actually
-- generated.

with po_headers as (

    select * from {{ ref('stg_purchase_order_headers') }}

),

po_lines as (

    select * from {{ ref('stg_purchase_order_lines') }}

),

dim_date as (

    select * from {{ ref('dim_date') }}

),

dim_vendor as (

    select * from {{ ref('dim_vendor') }}

),

dim_product as (

    select * from {{ ref('dim_product') }}

),

dim_employee as (

    select * from {{ ref('dim_employee') }}

),

dim_store_location as (

    select * from {{ ref('dim_store_location') }}

),

joined as (

    select
        po_lines.po_number,
        po_lines.line_number,
        dim_date.date_key,
        dim_vendor.vendor_key,
        dim_product.product_key,
        dim_product.product_category_key,
        dim_employee.employee_key,
        dim_store_location.store_key,
        po_lines.quantity_ordered,
        po_lines.unit_price,
        po_lines.extended_price,
        po_lines.discount_amount,
        po_lines.net_purchase_amount

    from po_lines

    inner join po_headers
        on po_lines.po_number = po_headers.po_number

    left join dim_date
        on to_char(po_headers.order_date, 'YYYYMMDD')::int = dim_date.date_key

    left join dim_vendor
        on po_headers.vendor_name = dim_vendor.vendor_name

    left join dim_product
        on po_lines.product_business_key = dim_product.product_business_key

    left join dim_employee
        on po_headers.employee_id = dim_employee.employee_id

    left join dim_store_location
        on po_headers.store_id = dim_store_location.store_id

)

select
    {{ dbt_utils.generate_surrogate_key(['po_number', 'line_number']) }} as purchasing_key,
    po_number,
    date_key,
    vendor_key,
    product_key,
    product_category_key,
    employee_key,
    store_key,
    quantity_ordered,
    unit_price,
    extended_price,
    discount_amount,
    net_purchase_amount

from joined 