-- dim_date: generated calendar dimension covering the full 2025 mock
-- data range. Uses dbt_utils.date_spine to produce one row per day —
-- this isn't sourced from any raw table, since a date dimension is
-- conventionally generated rather than pulled from an operational
-- system.
--
-- date_key uses the common "smart key" convention (YYYYMMDD as an
-- integer) rather than a hashed surrogate key — this is standard
-- practice for date dimensions specifically, since it's human-readable
-- and sorts naturally.

with date_spine as (

    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2025-01-01' as date)",
        end_date="cast('2026-01-01' as date)"
    ) }}

),

enriched as (

    select
        date_day,
        to_char(date_day, 'YYYYMMDD')::int   as date_key,
        dayname(date_day)                    as day_of_week_name,
        dayofweek(date_day)                  as day_of_week_number,   -- 0=Sunday ... 6=Saturday
        dayofmonth(date_day)                 as day_of_month,
        month(date_day)                      as month_number,
        monthname(date_day)                  as month_name,
        quarter(date_day)                    as quarter_number,
        year(date_day)                       as year_number,
        case
            when dayofweek(date_day) in (0, 6) then true
            else false
        end                                   as is_weekend

    from date_spine

)

select
    date_key,
    date_day as full_date,
    day_of_week_name,
    day_of_week_number,
    day_of_month,
    month_number,
    month_name,
    quarter_number,
    year_number,
    is_weekend

from enriched 