-- A query to calculate cost of goods sold for every month of the 12 month period of mock data
-- To be run in the Snowflake workspace with data transformed by dbt into the "analytics" warehouse
with monthly_inventory as (

    select
        dd.year_number,
        dd.month_number,
        dd.month_name,
        sum(fiv.inventory_value) as ending_inventory_value

    from analytics.dbt_rmasson.fact_inventory_valuation fiv
    join analytics.dbt_rmasson.dim_date dd
        on fiv.date_key = dd.date_key

    group by dd.year_number, dd.month_number, dd.month_name

),

monthly_purchases as (

    select
        dd.year_number,
        dd.month_number,
        sum(fp.net_purchase_amount) as total_purchases_value

    from analytics.dbt_rmasson.fact_purchasing fp
    join analytics.dbt_rmasson.dim_date dd
        on fp.date_key = dd.date_key

    group by dd.year_number, dd.month_number

),

combined as (

    select
        mi.year_number,
        mi.month_number,
        mi.month_name,
        mi.ending_inventory_value,
        mp.total_purchases_value,
        lag(mi.ending_inventory_value) over (
            order by mi.year_number, mi.month_number
        ) as beginning_inventory_value

    from monthly_inventory mi
    left join monthly_purchases mp
        on mi.year_number = mp.year_number
        and mi.month_number = mp.month_number

)

select
    year_number,
    month_number,
    month_name,
    beginning_inventory_value,
    total_purchases_value,
    ending_inventory_value,
    beginning_inventory_value + total_purchases_value - ending_inventory_value as monthly_cogs

from combined
order by year_number, month_number