-- Staging model: light cleanup of raw purchase order headers.
-- One row per purchase order (Purchasing header grain).

with source as (

    select * from {{ source('operations', 'purchase_order_headers') }}

), 

renamed as (

    select
        po_number,
        order_date,
        vendor                      as vendor_name,
        employee_id,
        employee_name,
        employee_role,
        store_id,
        store_name,
        buy_method                  as order_method

    from source

)

select * from renamed