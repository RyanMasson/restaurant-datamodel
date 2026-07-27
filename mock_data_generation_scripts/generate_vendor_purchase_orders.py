"""
generate_vendor_purchase_orders.py

Generates mock "vendor purchase order" source data, mimicking what a
restaurant's ordering system (app / text / website-based vendor ordering)
would produce. Mirrors the real-world pattern of normalized source
systems: a header file (one row per PO) and a line-item file (one row
per product ordered on that PO) — matching the Purchasing business
process grain: "row is each line item per purchase order made to a
vendor."

Reads: master_product_list.csv (must be generated first, via
       generate_master_product_list.py)
Outputs: purchase_order_headers.csv
         purchase_order_lines.csv

NOTE ON PLACEHOLDER DIMENSIONS:
The Employee and Store Location master files haven't been generated yet
in this project, so this script uses small embedded placeholder lists
for "who placed the order" and "which store" so the Purchasing fact
grain is fully populated. Once dedicated Employee Roster and Store
Location generator scripts exist, swap these placeholders out for reads
from those CSVs to keep everything conformed.
"""

import csv
import random
from datetime import date, timedelta

random.seed(42)  # reproducible output

# ---------------------------------------------------------------------
# Vendor pool — kept identical to generate_master_product_list.py so
# vendor names match exactly across source systems (conformed dimension)
# ---------------------------------------------------------------------
VENDORS = [
    "Sysco", "US Foods", "Performance Foodservice", "Ben E. Keith",
    "Restaurant Depot", "Chef's Warehouse", "Gordon Food Service",
    "Shamrock Foods", "Reinhart FoodService", "Southern Wine & Spirits",
    "Breakthru Beverage", "Republic National Distributing",
    "Cheney Brothers", "Fresh Point", "US Beverage Supply",
]

# ---------------------------------------------------------------------
# Buy methods — how the order was placed with the vendor
# (kept identical to generate_master_product_list.py)
# ---------------------------------------------------------------------
BUY_METHODS = ["Vendor App", "Text Message", "Website"]

# ---------------------------------------------------------------------
# Placeholder Employee list — employees authorized to place orders
# (stand-in until a dedicated Employee Roster generator exists)
# ---------------------------------------------------------------------
EMPLOYEES = [
    ("EMP-001", "Dana Ruiz", "General Manager"),
    ("EMP-002", "Marcus Lee", "Kitchen Manager"),
    ("EMP-003", "Priya Nair", "Sous Chef"),
    ("EMP-004", "Jordan Blake", "Bar Manager"),
    ("EMP-005", "Sam Whitfield", "Assistant Manager"),
]

# ---------------------------------------------------------------------
# Placeholder Store Location — single-location restaurant assumption
# (stand-in until a dedicated Store Location generator exists)
# ---------------------------------------------------------------------
STORE_LOCATIONS = [
    ("STORE-01", "Main Street Location"),
]

# ---------------------------------------------------------------------
# Date range for generated purchase orders
# ---------------------------------------------------------------------
START_DATE = date(2025, 1, 6)   # first Monday of the range
END_DATE = date(2025, 12, 28)   # last Monday of the range

# Probability a given vendor places an order in a given week
# (roughly every 2-3 weeks per vendor on average)
WEEKLY_ORDER_PROBABILITY = 0.35


def load_products(path="master_product_list.csv"):
    """Load the master product list and build a vendor -> products map."""
    products = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)

    vendor_products = {vendor: [] for vendor in VENDORS}
    for product in products:
        primary = product["Primary Vendor"]
        secondary = product["Secondary Vendor"]
        if primary in vendor_products:
            vendor_products[primary].append(product)
        if secondary in vendor_products:
            vendor_products[secondary].append(product)

    return vendor_products


def week_start_dates(start, end):
    """Yield each Monday from start to end, inclusive."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=7)


def random_weekday_in_week(monday):
    """Pick a random weekday (Mon-Fri) within the week starting on `monday`."""
    offset = random.randint(0, 4)
    return monday + timedelta(days=offset)


def generate_purchase_orders(vendor_products):
    headers = []
    lines = []
    po_counter = 1
    line_counter = 1

    for monday in week_start_dates(START_DATE, END_DATE):
        for vendor in VENDORS:
            available_products = vendor_products.get(vendor, [])
            if not available_products:
                continue
            if random.random() > WEEKLY_ORDER_PROBABILITY:
                continue

            po_number = f"PO-{po_counter:05d}"
            po_counter += 1

            order_date = random_weekday_in_week(monday)
            employee_id, employee_name, employee_role = random.choice(EMPLOYEES)
            store_id, store_name = random.choice(STORE_LOCATIONS)
            buy_method = random.choice(BUY_METHODS)

            headers.append({
                "PO Number": po_number,
                "Order Date": order_date.isoformat(),
                "Vendor": vendor,
                "Employee ID": employee_id,
                "Employee Name": employee_name,
                "Employee Role": employee_role,
                "Store ID": store_id,
                "Store Name": store_name,
                "Buy Method": buy_method,
            })

            num_lines = min(len(available_products), random.randint(3, 8))
            line_products = random.sample(available_products, num_lines)

            for line_num, product in enumerate(line_products, start=1):
                wholesale_price = float(product["Wholesale Price"])
                unit_price = round(wholesale_price * random.uniform(0.95, 1.05), 2)
                quantity_ordered = random.randint(1, 10)
                extended_price = round(unit_price * quantity_ordered, 2)

                has_discount = random.random() < 0.15
                discount_amount = round(extended_price * random.uniform(0.02, 0.08), 2) if has_discount else 0.0
                net_purchase_amount = round(extended_price - discount_amount, 2)

                lines.append({
                    "PO Number": po_number,
                    "Line Number": line_num,
                    "Product Primary Key": product["Primary Key"],
                    "Item Name": product["Item Name"],
                    "Category": product["Category"],
                    "Subcategory": product["Subcategory"],
                    "Unit of Measure": product["Unit of Measure"],
                    "Quantity Ordered": quantity_ordered,
                    "Unit Price": unit_price,
                    "Extended Price": extended_price,
                    "Discount Amount": discount_amount,
                    "Net Purchase Amount": net_purchase_amount,
                })
                line_counter += 1

    return headers, lines


def write_csv(rows, fieldnames, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    vendor_products = load_products("master_product_list.csv")
    headers, lines = generate_purchase_orders(vendor_products)

    header_fields = [
        "PO Number", "Order Date", "Vendor", "Employee ID", "Employee Name",
        "Employee Role", "Store ID", "Store Name", "Buy Method",
    ]
    line_fields = [
        "PO Number", "Line Number", "Product Primary Key", "Item Name",
        "Category", "Subcategory", "Unit of Measure", "Quantity Ordered",
        "Unit Price", "Extended Price", "Discount Amount", "Net Purchase Amount",
    ]

    write_csv(headers, header_fields, "purchase_order_headers.csv")
    write_csv(lines, line_fields, "purchase_order_lines.csv")

    print(f"Generated {len(headers)} purchase orders -> purchase_order_headers.csv")
    print(f"Generated {len(lines)} PO line items -> purchase_order_lines.csv")


if __name__ == "__main__":
    main()
