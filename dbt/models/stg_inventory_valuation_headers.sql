-- Staging model: light cleanup of raw monthly inventory valuation headers.
-- One row per monthly inventory valuation (Inventory valuation header grain).

with source as (

    select * from {{ source('operations', 'inventory_valuation_headers') }}

),
 
renamed as (

    select
        valuation_id,
        inventory_date,
        store_id,
        store_name,
        counted_by,
        extended_by

    from source

)

select * from renamed