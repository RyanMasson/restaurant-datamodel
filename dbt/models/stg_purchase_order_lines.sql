-- Staging model: light cleanup of raw purchase order line items.
-- One row per line item per purchase order (Purchasing grain).

with source as (

    select * from {{ source('operations', 'purchase_order_lines') }}

),
 
renamed as (

    select
        po_number,
        line_number,
        product_primary_key          as product_business_key,
        item_name                    as product_name,
        category                     as product_category,
        subcategory                  as product_subcategory,
        unit_of_measure,
        quantity_ordered::number(10,2)     as quantity_ordered,
        unit_price::number(10,2)           as unit_price,
        extended_price::number(10,2)       as extended_price,
        discount_amount::number(10,2)      as discount_amount,
        net_purchase_amount::number(10,2)  as net_purchase_amount

    from source

)

select * from renamed