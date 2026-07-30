-- dim_order_channel: distinct order channels from the sales header table.

with sales_headers as (

    select * from {{ ref('stg_sales_order_headers') }}

),

distinct_channels as (

    select distinct order_channel
    from sales_headers

)

select
    {{ dbt_utils.generate_surrogate_key(['order_channel']) }} as channel_key,
    order_channel

from distinct_channels 