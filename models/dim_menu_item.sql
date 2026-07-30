-- dim_menu_item: current-state menu item dimension.
--
-- SCOPE NOTE: this takes only each item's most recent monthly extract,
-- rather than tracking full price/status history over time (SCD
-- Type 2). This is a deliberate simplification for this project —
-- historical price tracking was decided to be out of scope. If it's
-- ever needed later, the raw monthly extracts in
-- stg_menu_item_snapshots still contain the full history to rebuild
-- from.

with snapshots as (

    select * from {{ ref('stg_menu_item_snapshots') }}

),

most_recent_per_item as (

    select
        *,
        row_number() over (
            partition by menu_item_business_key
            order by extract_date desc
        ) as recency_rank

    from snapshots

)

select
    {{ dbt_utils.generate_surrogate_key(['menu_item_business_key']) }} as menu_item_key,
    menu_item_business_key,
    menu_item_pos_code,
    menu_item_name,
    menu_item_category,
    menu_item_subcategory,
    price,
    description,
    is_active,
    is_vegetarian,
    is_vegan,
    is_gluten_free

from most_recent_per_item
where recency_rank = 1