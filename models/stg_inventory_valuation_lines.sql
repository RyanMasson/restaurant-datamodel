-- Staging model: light cleanup of raw monthly inventory valuation line items.
-- One row per product per monthly inventory valuation (Inventory valuation grain).

with source as (

    select * from {{ source('operations', 'inventory_valuation_lines') }}

),

renamed as (

    select
        valuation_id,
        item_primary_key             as product_business_key,
        item                         as product_name,
        category                     as product_category,
        subcategory                  as product_subcategory,
        unit                         as unit_of_measure,
        item_amount::number(10,2)       as item_amount,
        item_unit_value::number(10,2)   as item_unit_value,
        inventory_value::number(10,2)   as inventory_value

    from source

)

select * from renamed 