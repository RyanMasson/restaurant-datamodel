-- dim_product: one row per product, referencing dim_product_category.

with products as (

    select * from {{ ref('stg_master_product_list') }}

),

categories as (

    select * from {{ ref('dim_product_category') }}

),

joined as (

    select
        products.product_business_key,
        products.product_name,
        products.unit_of_measure,
        products.wholesale_price,
        products.primary_vendor,
        products.secondary_vendor,
        products.order_method,
        products.description,
        categories.product_category_key

    from products
    left join categories
        on products.product_category = categories.product_category
        and products.product_subcategory = categories.product_subcategory

)

select
    {{ dbt_utils.generate_surrogate_key(['product_business_key']) }} as product_key,
    product_business_key,
    product_category_key,
    product_name,
    unit_of_measure,
    wholesale_price,
    primary_vendor,
    secondary_vendor,
    order_method,
    description

from joined 