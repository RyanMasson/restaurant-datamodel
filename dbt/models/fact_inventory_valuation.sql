-- fact_inventory_valuation: grain is one row per product per monthly
-- inventory valuation.
--
-- NOTE: Counted By / Extended By in the raw data are plain employee
-- names, not employee IDs (a known gap flagged back when dim_employee
-- was built). This model resolves them to employee_key by matching on
-- employee_name instead of employee_id — functional given the mock
-- data's placeholder employee list, but worth calling out as a
-- fragile join (name matching is far less robust than ID matching in
-- a real system with employee turnover or name changes).

with inv_headers as (

    select * from {{ ref('stg_inventory_valuation_headers') }}

),

inv_lines as (

    select * from {{ ref('stg_inventory_valuation_lines') }}

),

dim_date as (

    select * from {{ ref('dim_date') }}

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
        inv_lines.valuation_id,
        inv_lines.product_business_key,
        dim_date.date_key,
        dim_product.product_key,
        dim_product.product_category_key,
        counted_by_employee.employee_key as counted_by_employee_key,
        extended_by_employee.employee_key as extended_by_employee_key,
        dim_store_location.store_key,
        inv_lines.item_amount,
        inv_lines.item_unit_value,
        inv_lines.inventory_value

    from inv_lines

    inner join inv_headers
        on inv_lines.valuation_id = inv_headers.valuation_id

    left join dim_date
        on to_char(inv_headers.inventory_date, 'YYYYMMDD')::int = dim_date.date_key

    left join dim_product
        on inv_lines.product_business_key = dim_product.product_business_key

    left join dim_employee as counted_by_employee
        on inv_headers.counted_by = counted_by_employee.employee_name

    left join dim_employee as extended_by_employee
        on inv_headers.extended_by = extended_by_employee.employee_name

    left join dim_store_location
        on inv_headers.store_id = dim_store_location.store_id

)

select
    {{ dbt_utils.generate_surrogate_key(['valuation_id', 'product_business_key']) }} as inventory_valuation_key,
    valuation_id,
    date_key,
    product_key,
    product_category_key,
    counted_by_employee_key,
    extended_by_employee_key,
    store_key,
    item_amount,
    item_unit_value,
    inventory_value

from joined 