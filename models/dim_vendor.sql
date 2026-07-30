-- dim_vendor: distinct vendor names, unioned from the primary and
-- secondary vendor columns on the product master list (vendors aren't
-- their own source file in this project — they only show up as
-- attributes on products).

with products as (

    select * from {{ ref('stg_master_product_list') }}

),

primary_vendors as (

    select primary_vendor as vendor_name
    from products

),

secondary_vendors as (

    select secondary_vendor as vendor_name
    from products

),

unioned as (

    select * from primary_vendors
    union
    select * from secondary_vendors

)

select
    {{ dbt_utils.generate_surrogate_key(['vendor_name']) }} as vendor_key,
    vendor_name

from unioned
where vendor_name is not null 