-- dim_employee: distinct employees, unioned from the header tables
-- that carry employee_id/employee_name (Purchasing and Sales).
--
-- NOTE: Inventory valuation headers only carry Counted By/Extended By
-- as plain names (no employee_id), since that's how the mock data was
-- generated. Those two columns can't be resolved to employee_key by
-- ID the way Purchasing/Sales can — joining them to this dimension
-- would need to match on employee_name instead, which is a known
-- limitation worth calling out in the project write-up rather than
-- silently working around here.

with purchasing_employees as (

    select
        employee_id,
        employee_name,
        employee_role

    from {{ ref('stg_purchase_order_headers') }}

),

sales_employees as (

    select
        employee_id,
        employee_name,
        cast(null as varchar) as employee_role

    from {{ ref('stg_sales_order_headers') }}

),

combined as (

    select * from purchasing_employees
    union all
    select * from sales_employees

),

deduped as (

    select
        employee_id,
        employee_name,
        max(employee_role) as employee_role

    from combined
    group by employee_id, employee_name

)

select
    {{ dbt_utils.generate_surrogate_key(['employee_id']) }} as employee_key,
    employee_id,
    employee_name,
    employee_role

from deduped 