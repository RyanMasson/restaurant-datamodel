-- fact_sales: grain is one row per menu item per order ticket.
-- Joins sales header + line staging models to dimensions, resolving
-- natural keys to surrogate keys.

with sales_headers as (

    select * from {{ ref('stg_sales_order_headers') }}

),

sales_lines as (

    select * from {{ ref('stg_sales_order_lines') }}

),

dim_date as (

    select * from {{ ref('dim_date') }}

),

dim_time_of_day as (

    select * from {{ ref('dim_time_of_day') }}

),

dim_employee as (

    select * from {{ ref('dim_employee') }}

),

dim_menu_item as (

    select * from {{ ref('dim_menu_item') }}

),

dim_order_channel as (

    select * from {{ ref('dim_order_channel') }}

),

dim_store_location as (

    select * from {{ ref('dim_store_location') }}

),

joined as (

    select
        sales_lines.order_ticket_number,
        sales_lines.line_number,
        dim_date.date_key,
        dim_time_of_day.time_key,
        dim_employee.employee_key,
        dim_menu_item.menu_item_key,
        dim_order_channel.channel_key,
        dim_store_location.store_key,
        sales_lines.quantity_sold,
        sales_lines.unit_price,
        sales_lines.extended_price,
        sales_lines.discount_amount,
        sales_lines.net_sales_amount

    from sales_lines

    inner join sales_headers
        on sales_lines.order_ticket_number = sales_headers.order_ticket_number

    left join dim_date
        on to_char(sales_headers.order_timestamp::date, 'YYYYMMDD')::int = dim_date.date_key

    left join dim_time_of_day
        on hour(sales_headers.order_timestamp) = dim_time_of_day.hour_of_day

    left join dim_employee
        on sales_headers.employee_id = dim_employee.employee_id

    left join dim_menu_item
        on sales_lines.menu_item_pos_code = dim_menu_item.menu_item_pos_code

    left join dim_order_channel
        on sales_headers.order_channel = dim_order_channel.order_channel

    left join dim_store_location
        on sales_headers.store_id = dim_store_location.store_id

)

select
    {{ dbt_utils.generate_surrogate_key(['order_ticket_number', 'line_number']) }} as sales_key,
    order_ticket_number,
    date_key,
    time_key,
    employee_key,
    menu_item_key,
    channel_key,
    store_key,
    quantity_sold,
    unit_price,
    extended_price,
    discount_amount,
    net_sales_amount

from joined 