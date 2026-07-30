-- Staging model: light cleanup of the raw monthly menu item snapshots.
-- Still one row per item per monthly extract at this point — the
-- SCD Type 2 collapsing into effective/expiration dates happens later,
-- in the dbt snapshot that reads from this model, not here.

with source as (

    select * from {{ source('operations', 'menu_item_snapshots') }}

),

renamed as (

    select
        business_key                as menu_item_business_key,
        pos_code                    as menu_item_pos_code,
        extract_date,
        menu_item_name,
        category                    as menu_item_category,
        subcategory                 as menu_item_subcategory,
        price::number(10,2)         as price,
        description,
        is_active,
        is_vegetarian,
        is_vegan,
        is_gluten_free

    from source

)

select * from renamed 