-- dim_product_category: distinct product category/subcategory pairs.

with products as (

    select * from {{ ref('stg_master_product_list') }}

),

distinct_categories as (

    select distinct
        product_category,
        product_subcategory

    from products

)

select
    {{ dbt_utils.generate_surrogate_key(['product_category', 'product_subcategory']) }} as product_category_key,
    product_category,
    product_subcategory

from distinct_categories 