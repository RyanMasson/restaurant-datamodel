-- dim_store_location: distinct store locations, unioned across all
-- three business process header tables that carry store_id/store_name.

with purchasing_stores as (

    select store_id, store_name from {{ ref('stg_purchase_order_headers') }}

),

inventory_stores as (

    select store_id, store_name from {{ ref('stg_inventory_valuation_headers') }}

),

sales_stores as (

    select store_id, store_name from {{ ref('stg_sales_order_headers') }}

),

combined as (

    select * from purchasing_stores
    union
    select * from inventory_stores
    union
    select * from sales_stores

)

select
    {{ dbt_utils.generate_surrogate_key(['store_id']) }} as store_key,
    store_id,
    store_name

from combined 