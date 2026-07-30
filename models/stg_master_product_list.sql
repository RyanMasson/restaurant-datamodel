-- Staging model: light cleanup of the raw master product list.
-- No business logic, joins, or aggregation here — just renaming and
-- casting so downstream models (dim_product, dim_product_category)
-- have consistent, well-named columns to build from.

with source as (

    select * from {{ source('operations', 'master_product_list') }}

),

renamed as (

    select
        primary_key                as product_business_key,
        category                   as product_category,
        subcategory                as product_subcategory,
        item_name                   as product_name,
        unit_of_measure,
        wholesale_price::number(10,2) as wholesale_price,
        primary_vendor,
        secondary_vendor,
        buy_method                  as order_method,
        description

    from source

)

select * from renamed