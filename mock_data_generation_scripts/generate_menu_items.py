"""
generate_menu_items.py

Author: Ryan Masson
Part of: Restaurant Data Model project

Generates a mock "Menu Item Master" export — mimicking a periodic full
export from a restaurant's menu/POS management system, NOT a
pre-built SCD Type 2 dimension table. 

Output: menu_item_snapshots.csv
Columns: Extract Date, Business Key, POS Code, Menu Item Name, Category,
         Subcategory, Price, Description, Is Active, Is Vegetarian,
         Is Vegan, Is Gluten Free

DIETARY FLAG NOTE:
Is Vegetarian / Is Vegan / Is Gluten Free are inferred from keyword
matching against the item name and description. This is a simplified
heuristic for mock data purposes, not a real allergen/recipe analysis —
edge cases (e.g. a "gluten-free bun" substitution) won't be caught.
"""

import csv
import random
from datetime import date

random.seed(42)  # reproducible output

# ---------------------------------------------------------------------
# Monthly extract dates — simulating a menu system export pulled on
# the first of each month throughout 2025
# ---------------------------------------------------------------------
EXTRACT_DATES = [
    date(2025, 1, 1), date(2025, 2, 1), date(2025, 3, 1), date(2025, 4, 1),
    date(2025, 5, 1), date(2025, 6, 1), date(2025, 7, 1), date(2025, 8, 1),
    date(2025, 9, 1), date(2025, 10, 1), date(2025, 11, 1), date(2025, 12, 1),
]

# ---------------------------------------------------------------------
# Subcategory -> Category mapping
# ---------------------------------------------------------------------
SUBCATEGORY_TO_CATEGORY = {
    "Appetizer": "Food",
    "Entree": "Food",
    "Side": "Food",
    "Non-Alcoholic": "Beverage",
    "Alcoholic": "Beverage",
}

# ---------------------------------------------------------------------
# Business key prefixes per subcategory
# ---------------------------------------------------------------------
SUBCATEGORY_PREFIX = {
    "Appetizer": "APP",
    "Entree": "ENT",
    "Side": "SID",
    "Non-Alcoholic": "NAB",
    "Alcoholic": "ALC",
}

# ---------------------------------------------------------------------
# Menu item definitions per subcategory.
# Each entry: (Item Name, Price, Description)
# ---------------------------------------------------------------------
MENU_ITEMS = {
    "Appetizer": [
        ("Crispy Calamari", 13.50, "Fried calamari with marinara and lemon aioli"),
        ("Loaded Nachos", 12.00, "Tortilla chips with cheese, jalapeños, and pico de gallo"),
        ("Buffalo Wings", 14.00, "Crispy chicken wings tossed in buffalo sauce"),
        ("Spinach Artichoke Dip", 11.50, "Warm dip served with tortilla chips"),
        ("Mozzarella Sticks", 10.00, "Breaded mozzarella with marinara sauce"),
        ("Shrimp Cocktail", 15.00, "Chilled shrimp with house cocktail sauce"),
        ("Bruschetta", 9.50, "Toasted baguette with tomato, basil, and balsamic"),
        ("Pretzel Bites", 9.00, "Soft pretzel bites with beer cheese dip"),
        ("Loaded Potato Skins", 11.00, "Potato skins with bacon, cheddar, and sour cream"),
        ("Ahi Tuna Tartare", 16.50, "Sesame-crusted ahi tuna with avocado and soy glaze"),
        ("Onion Rings", 8.50, "Beer-battered onion rings with chipotle ranch"),
        ("Caprese Skewers", 10.50, "Mozzarella, cherry tomato, and basil skewers"),
        ("Deviled Eggs", 8.00, "Classic deviled eggs with smoked paprika"),
        ("Egg Rolls", 9.50, "Vegetable egg rolls with sweet chili sauce"),
        ("Charcuterie Board", 18.00, "Selection of cured meats, cheese, and crackers"),
    ],
    "Entree": [
        ("Classic Cheeseburger", 15.00, "Beef patty with cheddar, lettuce, tomato, and fries"),
        ("Grilled Salmon", 24.00, "Grilled salmon with seasonal vegetables"),
        ("Chicken Parmesan", 19.50, "Breaded chicken with marinara and mozzarella over pasta"),
        ("NY Strip Steak", 28.00, "Grilled NY strip with garlic butter and mashed potatoes"),
        ("Fish and Chips", 17.50, "Beer-battered cod with fries and tartar sauce"),
        ("BBQ Ribs", 23.00, "Slow-cooked ribs with house BBQ sauce and coleslaw"),
        ("Margherita Pizza", 16.00, "Tomato, fresh mozzarella, and basil"),
        ("Pepperoni Pizza", 17.00, "Classic pepperoni and mozzarella"),
        ("Fettuccine Alfredo", 16.50, "Fettuccine in creamy parmesan sauce"),
        ("Shrimp Scampi", 21.00, "Shrimp sautéed in garlic butter over linguine"),
        ("Vegetable Stir Fry", 15.50, "Seasonal vegetables in a soy-ginger sauce over rice"),
        ("Chicken Caesar Salad", 14.50, "Grilled chicken, romaine, parmesan, and Caesar dressing"),
        ("Cobb Salad", 14.00, "Chicken, bacon, egg, avocado, and blue cheese"),
        ("Turkey Club Sandwich", 13.50, "Turkey, bacon, lettuce, and tomato on toasted bread"),
        ("Veggie Burger", 14.50, "Plant-based patty with lettuce, tomato, and fries"),
        ("Pork Chop", 22.00, "Grilled pork chop with apple chutney and mashed potatoes"),
        ("Lobster Roll", 26.00, "Chilled lobster salad on a toasted bun with fries"),
        ("Chicken Fajitas", 18.50, "Grilled chicken and peppers with tortillas and rice"),
        ("Beef Tacos", 15.00, "Three tacos with beef, salsa, and cotija cheese"),
        ("Eggplant Parmesan", 16.00, "Breaded eggplant with marinara and mozzarella"),
    ],
    "Side": [
        ("French Fries", 5.00, "Crispy golden French fries"),
        ("Sweet Potato Fries", 6.00, "Crispy sweet potato fries with honey aioli"),
        ("Side Salad", 5.50, "Mixed greens with house dressing"),
        ("Mashed Potatoes", 5.50, "Creamy mashed potatoes with gravy"),
        ("Steamed Broccoli", 5.00, "Steamed broccoli with lemon butter"),
        ("Mac and Cheese", 6.50, "Creamy three-cheese macaroni"),
        ("Coleslaw", 4.50, "Classic creamy coleslaw"),
        ("Rice Pilaf", 5.00, "Seasoned rice pilaf"),
        ("Onion Rings (side)", 6.00, "Beer-battered onion rings"),
        ("Grilled Vegetables", 6.50, "Seasonal grilled vegetable medley"),
        ("Garlic Bread", 5.00, "Toasted bread with garlic butter"),
        ("Baked Beans", 4.50, "Slow-cooked baked beans"),
    ],
    "Non-Alcoholic": [
        ("Fountain Soda", 3.50, "Choice of Coca-Cola fountain beverages"),
        ("Iced Tea", 3.50, "Freshly brewed iced tea"),
        ("Lemonade", 4.00, "Fresh-squeezed lemonade"),
        ("Coffee", 3.75, "Freshly brewed regular or decaf coffee"),
        ("Hot Tea", 3.75, "Selection of hot teas"),
        ("Sparkling Water", 4.50, "Bottled sparkling mineral water"),
        ("Orange Juice", 4.50, "Fresh-squeezed orange juice"),
        ("Milkshake", 6.50, "Hand-spun vanilla, chocolate, or strawberry shake"),
        ("Mocktail - Virgin Mojito", 6.00, "Lime, mint, and soda, alcohol-free"),
        ("Hot Chocolate", 4.00, "Rich hot chocolate topped with whipped cream"),
    ],
    "Alcoholic": [
        ("Draft Beer", 7.00, "Rotating domestic and craft draft selection"),
        ("Bottled Beer", 6.50, "Selection of domestic and imported bottles"),
        ("House Red Wine", 9.00, "Glass of house Cabernet Sauvignon"),
        ("House White Wine", 9.00, "Glass of house Chardonnay"),
        ("Classic Margarita", 11.00, "Tequila, triple sec, and lime"),
        ("Old Fashioned", 12.00, "Bourbon, bitters, and orange twist"),
        ("Mojito", 11.00, "White rum, mint, lime, and soda"),
        ("Espresso Martini", 13.00, "Vodka, coffee liqueur, and espresso"),
        ("Moscow Mule", 11.50, "Vodka, ginger beer, and lime"),
        ("Sangria", 9.50, "House red sangria with seasonal fruit"),
        ("Prosecco (glass)", 9.00, "Glass of sparkling Prosecco"),
        ("Whiskey Sour", 11.50, "Whiskey, lemon, and simple syrup"),
    ],
}


MEAT_SEAFOOD_KEYWORDS = [
    "chicken", "beef", "steak", "salmon", "shrimp", "bacon", "pork",
    "lobster", "calamari", "tuna", "turkey", "ribs", "cod", "wing", "fish",
]
DAIRY_EGG_KEYWORDS = [
    "cheese", "cheddar", "mozzarella", "parmesan", "cream", "butter",
    "milk", "egg", "aioli", "yogurt", "alfredo", "sour cream", "mayo",
]
GLUTEN_KEYWORDS = [
    "bread", "bun", "pasta", "fettuccine", "linguine", "pizza", "tortilla",
    "dough", "pretzel", "batter", "breaded", "noodle", "cake", "crust",
    "roll", "sandwich", "taco", "burger", "crouton", "beer", "wing",
    "calamari", "onion ring", "mac and cheese", "egg roll",
]


def infer_dietary_flags(name, description):
    """Simple keyword-based heuristic — see DIETARY FLAG NOTE above."""
    text = f"{name} {description}".lower()
    is_vegetarian = not any(k in text for k in MEAT_SEAFOOD_KEYWORDS)
    is_vegan = is_vegetarian and not any(k in text for k in DAIRY_EGG_KEYWORDS)
    is_gluten_free = not any(k in text for k in GLUTEN_KEYWORDS)
    return is_vegetarian, is_vegan, is_gluten_free


def generate_rows():
    rows = []
    pos_code = 1001

    for subcategory, items in MENU_ITEMS.items():
        category = SUBCATEGORY_TO_CATEGORY[subcategory]
        prefix = SUBCATEGORY_PREFIX[subcategory]

        for i, (name, price, description) in enumerate(items, start=1):
            business_key = f"{prefix}-{i:03d}"
            is_vegetarian, is_vegan, is_gluten_free = infer_dietary_flags(name, description)
            item_pos_code = pos_code
            pos_code += 1

            # Simulate a mid-year price increase for ~20% of items
            has_price_change = random.random() < 0.20
            change_month_index = random.randint(2, 9) if has_price_change else None  # March-Oct
            old_price = round(price * random.uniform(0.85, 0.95), 2) if has_price_change else None

            # Simulate discontinuation partway through the year for ~5% of items
            gets_discontinued = random.random() < 0.05
            discontinue_month_index = random.randint(4, 10) if gets_discontinued else None  # May-Nov

            for month_index, extract_date in enumerate(EXTRACT_DATES):
                if has_price_change and month_index < change_month_index:
                    current_price = old_price
                else:
                    current_price = price

                if gets_discontinued and month_index >= discontinue_month_index:
                    is_active = False
                else:
                    is_active = True

                rows.append({
                    "Extract Date": extract_date.isoformat(),
                    "Business Key": business_key,
                    "POS Code": item_pos_code,
                    "Menu Item Name": name,
                    "Category": category,
                    "Subcategory": subcategory,
                    "Price": current_price,
                    "Description": description,
                    "Is Active": is_active,
                    "Is Vegetarian": is_vegetarian,
                    "Is Vegan": is_vegan,
                    "Is Gluten Free": is_gluten_free,
                })

    return rows


def main(output_path="menu_item_snapshots.csv"):
    rows = generate_rows()
    fieldnames = [
        "Extract Date", "Business Key", "POS Code", "Menu Item Name",
        "Category", "Subcategory", "Price", "Description", "Is Active",
        "Is Vegetarian", "Is Vegan", "Is Gluten Free",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    num_items = sum(len(items) for items in MENU_ITEMS.values())
    print(f"Generated {len(rows)} rows ({num_items} items x {len(EXTRACT_DATES)} monthly extracts) -> {output_path}")


if __name__ == "__main__":
    main()
