-- Staging model: light cleanup of raw POS sales order line items.
-- One row per menu item per order ticket (Sales grain).

with source as (

    select * from {{ source('operations', 'sales_order_lines') }}

),

renamed as (

    select
        order_ticket_number,
        line_number,
        menu_item_pos_code,
        menu_item_name,
        category                    as menu_item_category,
        subcategory                 as menu_item_subcategory,
        quantity_sold::number(10,2)      as quantity_sold,
        unit_price::number(10,2)         as unit_price,
        extended_price::number(10,2)     as extended_price,
        discount_amount::number(10,2)    as discount_amount,
        net_sales_amount::number(10,2)   as net_sales_amount

    from source

)

select * from renamed 