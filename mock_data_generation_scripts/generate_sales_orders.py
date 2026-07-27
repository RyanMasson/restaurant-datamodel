"""
generate_sales_orders.py

Author: Ryan Masson
Part of: Restaurant Data Model project

Generates mock "POS Sales Order" source data — mimicking what a
restaurant's point-of-sale system would export, NOT the final Sales
fact table. Follows the same source-system-realistic pattern used for
Purchasing and Inventory: a header file (one row per order ticket) and
a line file (one row per menu item on that ticket), matching the
declared Sales grain: "row is each menu item per order ticket."

Reads: menu_item_snapshots.csv (must be generated first, via
       generate_menu_items.py)
Outputs: sales_order_headers.csv
         sales_order_lines.csv

SOURCE-SYSTEM REALISM NOTES:
- Order Timestamp is a single raw datetime, NOT pre-split into
  date_key/time_key — that split is ETL/dbt work, not something a POS
  system would hand you.
- Employee ID / Store ID / Menu Item POS Code are natural keys, not
  surrogate warehouse keys — resolving these to dimension surrogate
  keys happens downstream.
- Order Channel is a raw string (e.g. "DoorDash", "Dine In"), not a
  pre-resolved channel_key.
- Unit Price is looked up from the menu item's price AS OF the order
  date, using the monthly menu_item_snapshots.csv extracts — so a
  price that changed mid-year is correctly reflected before/after the
  change, and discontinued items stop appearing in sales after their
  discontinuation month, just like a real POS would.

NOTE ON PLACEHOLDER DIMENSIONS:
Employee ID/Name and Store ID/Name reuse the same placeholder lists
used in generate_vendor_purchase_orders.py and
generate_inventory_valuation.py, so the Employee and Store dimensions
stay conformed across all business processes in this project.
"""

import csv
import random
from datetime import date, datetime, timedelta

random.seed(42)  # reproducible output

# ---------------------------------------------------------------------
# Placeholder Employee list — kept identical to the other generator
# scripts so the Employee dimension conforms across all processes
# ---------------------------------------------------------------------
EMPLOYEES = [
    ("EMP-001", "Dana Ruiz", "General Manager"),
    ("EMP-002", "Marcus Lee", "Kitchen Manager"),
    ("EMP-003", "Priya Nair", "Sous Chef"),
    ("EMP-004", "Jordan Blake", "Bar Manager"),
    ("EMP-005", "Sam Whitfield", "Assistant Manager"),
]

# ---------------------------------------------------------------------
# Placeholder Store Location — kept identical to the other generator
# scripts (single-location assumption)
# ---------------------------------------------------------------------
STORE_ID, STORE_NAME = "STORE-01", "Main Street Location"

# ---------------------------------------------------------------------
# Order channels — raw strings, as a POS/ordering system would report
# them, weighted toward dine-in
# ---------------------------------------------------------------------
ORDER_CHANNELS = ["Dine In", "Takeout", "DoorDash", "Uber Eats", "Grubhub"]
ORDER_CHANNEL_WEIGHTS = [0.55, 0.15, 0.12, 0.10, 0.08]

# ---------------------------------------------------------------------
# Date range for generated sales — full year, matching the other
# monthly-grain processes
# ---------------------------------------------------------------------
START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)

# Average tickets/day by day-of-week (Mon=0 ... Sun=6) — weekends busier
AVG_TICKETS_BY_WEEKDAY = {
    0: 40, 1: 40, 2: 42, 3: 48,   # Mon-Thu
    4: 70, 5: 85, 6: 60,          # Fri, Sat, Sun
}


def load_menu_item_snapshots(path="menu_item_snapshots.csv"):
    """Build a per-item, date-sorted list of snapshot rows."""
    items = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.setdefault(row["Business Key"], []).append(row)

    for key in items:
        items[key].sort(key=lambda r: r["Extract Date"])

    return items


def get_item_state(item_snapshots, order_date_str):
    """Return the most recent snapshot on or before order_date_str."""
    applicable = [s for s in item_snapshots if s["Extract Date"] <= order_date_str]
    if not applicable:
        return None
    return applicable[-1]


def random_order_timestamp(order_date):
    """Pick a realistic order time, weighted toward lunch and dinner rushes."""
    period = random.choices(["lunch", "afternoon", "dinner", "late"], weights=[0.30, 0.10, 0.50, 0.10])[0]
    if period == "lunch":
        hour = random.randint(11, 13)
    elif period == "afternoon":
        hour = random.randint(14, 16)
    elif period == "dinner":
        hour = random.randint(17, 20)
    else:
        hour = random.randint(21, 22)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime(order_date.year, order_date.month, order_date.day, hour, minute, second)


def generate_sales(menu_items):
    headers = []
    lines = []
    ticket_counter = 1

    current_date = START_DATE
    while current_date <= END_DATE:
        order_date_str = current_date.isoformat()

        # Determine which items are active (sellable) as of this date
        active_items = []
        for business_key, snapshots in menu_items.items():
            state = get_item_state(snapshots, order_date_str)
            if state is not None and state["Is Active"] == "True":
                active_items.append(state)

        num_tickets = max(0, round(random.gauss(
            AVG_TICKETS_BY_WEEKDAY[current_date.weekday()],
            AVG_TICKETS_BY_WEEKDAY[current_date.weekday()] * 0.15
        )))

        for _ in range(num_tickets):
            ticket_number = f"TCK-{ticket_counter:06d}"
            ticket_counter += 1

            order_timestamp = random_order_timestamp(current_date)
            employee_id, employee_name, employee_role = random.choice(EMPLOYEES)
            channel = random.choices(ORDER_CHANNELS, weights=ORDER_CHANNEL_WEIGHTS)[0]

            headers.append({
                "Order Ticket Number": ticket_number,
                "Order Timestamp": order_timestamp.isoformat(sep=" "),
                "Employee ID": employee_id,
                "Employee Name": employee_name,
                "Store ID": STORE_ID,
                "Store Name": STORE_NAME,
                "Order Channel": channel,
            })

            num_line_items = random.randint(1, 5)
            line_items = random.sample(active_items, min(num_line_items, len(active_items)))

            for line_num, item in enumerate(line_items, start=1):
                unit_price = float(item["Price"])
                quantity_sold = random.randint(1, 3)
                extended_price = round(unit_price * quantity_sold, 2)

                has_discount = random.random() < 0.10  # ~10% of lines get a discount (comp, promo, etc.)
                discount_amount = round(extended_price * random.uniform(0.10, 0.25), 2) if has_discount else 0.0
                net_sales_amount = round(extended_price - discount_amount, 2)

                lines.append({
                    "Order Ticket Number": ticket_number,
                    "Line Number": line_num,
                    "Menu Item POS Code": item["POS Code"],
                    "Menu Item Name": item["Menu Item Name"],
                    "Category": item["Category"],
                    "Subcategory": item["Subcategory"],
                    "Quantity Sold": quantity_sold,
                    "Unit Price": unit_price,
                    "Extended Price": extended_price,
                    "Discount Amount": discount_amount,
                    "Net Sales Amount": net_sales_amount,
                })

        current_date += timedelta(days=1)

    return headers, lines


def write_csv(rows, fieldnames, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    menu_items = load_menu_item_snapshots("menu_item_snapshots.csv")
    headers, lines = generate_sales(menu_items)

    header_fields = [
        "Order Ticket Number", "Order Timestamp", "Employee ID", "Employee Name",
        "Store ID", "Store Name", "Order Channel",
    ]
    line_fields = [
        "Order Ticket Number", "Line Number", "Menu Item POS Code", "Menu Item Name",
        "Category", "Subcategory", "Quantity Sold", "Unit Price", "Extended Price",
        "Discount Amount", "Net Sales Amount",
    ]

    write_csv(headers, header_fields, "sales_order_headers.csv")
    write_csv(lines, line_fields, "sales_order_lines.csv")

    print(f"Generated {len(headers)} order tickets -> sales_order_headers.csv")
    print(f"Generated {len(lines)} order line items -> sales_order_lines.csv")


if __name__ == "__main__":
    main()
