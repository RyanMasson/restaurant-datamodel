-- dim_time_of_day: generated time-of-day dimension at HOURLY grain
-- (24 rows, one per hour of the day).
--
-- SCOPE NOTE: this is banded by hour rather than by minute. A true
-- minute-level dimension (1,440 rows) is the more "textbook" version,
-- but hourly banding is a common, reasonable simplification for meal-
-- period/peak-hour analysis, and keeps this dimension easy to reason
-- about. Order Timestamp on the Sales fact still retains full
-- minute/second precision if finer-grained analysis is ever needed —
-- this dimension is just for bucketing by hour and meal period.

with hours as (

    select
        row_number() over (order by seq4()) - 1 as hour_of_day
    from table(generator(rowcount => 24))

),

enriched as (

    select
        hour_of_day,
        case
            when hour_of_day between 11 and 13 then 'Lunch'
            when hour_of_day between 14 and 16 then 'Afternoon'
            when hour_of_day between 17 and 20 then 'Dinner'
            when hour_of_day between 21 and 22 then 'Late Night'
            else 'Closed'
        end as meal_period,
        case
            when hour_of_day in (12, 13, 18, 19, 20) then true
            else false
        end as is_peak_hours

    from hours

)

select
    hour_of_day as time_key,
    hour_of_day,
    meal_period,
    is_peak_hours

from enriched 