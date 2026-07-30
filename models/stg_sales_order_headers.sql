-- Staging model: light cleanup of raw POS sales order headers.
-- One row per order ticket (Sales header grain).

with source as (

    select * from {{ source('operations', 'sales_order_headers') }}

),
 
renamed as (

    select
        order_ticket_number,
        order_timestamp,
        employee_id,
        employee_name,
        store_id,
        store_name,
        order_channel

    from source

)

select * from renamed