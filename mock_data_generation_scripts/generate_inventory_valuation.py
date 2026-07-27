"""
generate_inventory_valuation.py

Generates mock "Inventory Valuation" source data, structured after the
inventory valuation sheet format in Food and Beverage Cost Control,
7th Edition (Wiley), p.121. Produces a header file (one row per monthly
valuation) and a line file (one row per product per valuation) —
matching the declared Inventory valuation grain: "row is each product
per monthly inventory valuation."

Reads: master_product_list.csv (must be generated first, via
       generate_master_product_list.py)
Outputs: inventory_valuation_headers.csv
         inventory_valuation_lines.csv

NOTE ON PLACEHOLDER DIMENSIONS:
Counted By / Extended By reuse the same placeholder Employee list and
single Store Location used in generate_vendor_purchase_orders.py, since
no dedicated Employee Roster / Store Location generator exists yet in
this project. Keeping the same names here means the Employee dimension
stays conformed across both business processes.
"""

import csv
import random
from datetime import date

random.seed(42)  # reproducible output

# ---------------------------------------------------------------------
# Placeholder Employee list — kept identical to
# generate_vendor_purchase_orders.py so the Employee dimension conforms
# across Purchasing and Inventory valuation
# ---------------------------------------------------------------------
EMPLOYEES = [
    ("EMP-001", "Dana Ruiz", "General Manager"),
    ("EMP-002", "Marcus Lee", "Kitchen Manager"),
    ("EMP-003", "Priya Nair", "Sous Chef"),
    ("EMP-004", "Jordan Blake", "Bar Manager"),
    ("EMP-005", "Sam Whitfield", "Assistant Manager"),
]

# ---------------------------------------------------------------------
# Placeholder Store Location — kept identical to
# generate_vendor_purchase_orders.py (single-location assumption)
# ---------------------------------------------------------------------
STORE_ID, STORE_NAME = "STORE-01", "Main Street Location"

# ---------------------------------------------------------------------
# Monthly valuation dates — last day of each month, 2025
# ---------------------------------------------------------------------
VALUATION_MONTHS = [
    date(2025, 1, 31), date(2025, 2, 28), date(2025, 3, 31),
    date(2025, 4, 30), date(2025, 5, 31), date(2025, 6, 30),
    date(2025, 7, 31), date(2025, 8, 31), date(2025, 9, 30),
    date(2025, 10, 31), date(2025, 11, 30), date(2025, 12, 31),
]

# ---------------------------------------------------------------------
# Typical on-hand quantity ranges by category (Item Amount), reflecting
# realistic stock levels — e.g. perishable Produce & Meat is kept low,
# Supplies are stocked in bulk
# ---------------------------------------------------------------------
ITEM_AMOUNT_RANGE = {
    "Non-Alcoholic Beverage": (5, 40),
    "Alcoholic Beverage": (3, 30),
    "Dry Goods & Spices": (5, 50),
    "Frozen/Refrigerated Goods": (5, 40),
    "Liquids/Pastes/Sauces": (3, 30),
    "Produce & Meat": (2, 25),
    "Supplies": (10, 100),
}


def load_products(path="master_product_list.csv"):
    products = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)
    return products


def generate_inventory_valuations(products):
    headers = []
    lines = []

    for month_index, valuation_date in enumerate(VALUATION_MONTHS, start=1):
        valuation_id = f"INV-2025-{month_index:02d}"

        counted_by, extended_by = random.sample(EMPLOYEES, 2)

        headers.append({
            "Valuation ID": valuation_id,
            "Inventory Date": valuation_date.isoformat(),
            "Store ID": STORE_ID,
            "Store Name": STORE_NAME,
            "Counted By": counted_by[1],
            "Extended By": extended_by[1],
        })

        for product in products:
            category = product["Category"]
            amount_range = ITEM_AMOUNT_RANGE.get(category, (5, 30))
            item_amount = random.randint(*amount_range)

            wholesale_price = float(product["Wholesale Price"])
            # simulate month-to-month price fluctuation around wholesale cost
            item_unit_value = round(wholesale_price * random.uniform(0.92, 1.08), 2)

            inventory_value = round(item_amount * item_unit_value, 2)

            lines.append({
                "Valuation ID": valuation_id,
                "Item": product["Item Name"],
                "Item Primary Key": product["Primary Key"],
                "Category": product["Category"],
                "Subcategory": product["Subcategory"],
                "Unit": product["Unit of Measure"],
                "Item Amount": item_amount,
                "Item Unit Value": item_unit_value,
                "Inventory Value": inventory_value,
            })

    return headers, lines


def write_csv(rows, fieldnames, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    products = load_products("master_product_list.csv")
    headers, lines = generate_inventory_valuations(products)

    header_fields = [
        "Valuation ID", "Inventory Date", "Store ID", "Store Name",
        "Counted By", "Extended By",
    ]
    line_fields = [
        "Valuation ID", "Item", "Item Primary Key", "Category", "Subcategory",
        "Unit", "Item Amount", "Item Unit Value", "Inventory Value",
    ]

    write_csv(headers, header_fields, "inventory_valuation_headers.csv")
    write_csv(lines, line_fields, "inventory_valuation_lines.csv")

    print(f"Generated {len(headers)} monthly valuations -> inventory_valuation_headers.csv")
    print(f"Generated {len(lines)} valuation line items -> inventory_valuation_lines.csv")


if __name__ == "__main__":
    main()
