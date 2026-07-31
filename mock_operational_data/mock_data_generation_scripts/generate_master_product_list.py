"""
generate_master_product_list.py

Author: Ryan Masson
Part of: Restaurant Data Model project

Generates a mock "Master Product List" CSV mimicking a restaurant's
product master file. The columns are taken from the real Google Sheet I used at work,
but all the rows are simulated with mock realistic restaurant data.

Output: master_product_list.csv
Columns: Category, Subcategory, Primary Key, Item Name, Unit of Measure,
         Wholesale Price, Primary Vendor, Secondary Vendor, Buy Method,
         Description
"""

import csv
import random

random.seed(42)  # reproducible output

# ---------------------------------------------------------------------
# Vendor pool (used to randomly assign Primary/Secondary Vendor)
# ---------------------------------------------------------------------
VENDORS = [
    "Sysco", "US Foods", "Performance Foodservice", "Ben E. Keith",
    "Restaurant Depot", "Chef's Warehouse", "Gordon Food Service",
    "Shamrock Foods", "Reinhart FoodService", "Southern Wine & Spirits",
    "Breakthru Beverage", "Republic National Distributing",
    "Cheney Brothers", "Fresh Point", "US Beverage Supply",
]

# ---------------------------------------------------------------------
# Buy methods — how the order is placed with the vendor
# ---------------------------------------------------------------------
BUY_METHODS = ["Vendor App", "Text Message", "Website"]

# ---------------------------------------------------------------------
# Product definitions per category.
# Each entry: (Subcategory, Item Name, Unit of Measure, Price Range,
#              Buy Method list, Description)
# ---------------------------------------------------------------------

PRODUCTS = {
    "Non-Alcoholic Beverage": [
        ("Soda", "Coca-Cola Syrup BIB", "5 gal bag-in-box", (55, 75), "Box", "Post-mix cola syrup concentrate"),
        ("Soda", "Diet Coke Syrup BIB", "5 gal bag-in-box", (55, 75), "Box", "Post-mix diet cola syrup concentrate"),
        ("Soda", "Sprite Syrup BIB", "5 gal bag-in-box", (55, 75), "Box", "Post-mix lemon-lime syrup concentrate"),
        ("Soda", "Ginger Ale Syrup BIB", "5 gal bag-in-box", (55, 75), "Box", "Post-mix ginger ale syrup concentrate"),
        ("Bottled Water", "Still Water 16.9oz", "case of 24", (6, 10), "Case", "Single-serve bottled still water"),
        ("Bottled Water", "Sparkling Water 12oz", "case of 24", (14, 20), "Case", "Single-serve sparkling mineral water"),
        ("Juice", "Orange Juice Concentrate", "gallon", (9, 14), "Gallon", "100% orange juice concentrate for fountain use"),
        ("Juice", "Cranberry Juice Cocktail", "gallon", (8, 12), "Gallon", "Sweetened cranberry juice cocktail"),
        ("Juice", "Pineapple Juice", "46 oz can", (3, 5), "Each", "Canned pineapple juice for cocktails and mocktails"),
        ("Juice", "Lemon Juice (bottled)", "32 oz bottle", (4, 7), "Bottle", "Shelf-stable reconstituted lemon juice"),
        ("Juice", "Lime Juice (bottled)", "32 oz bottle", (4, 7), "Bottle", "Shelf-stable reconstituted lime juice"),
        ("Coffee", "Espresso Beans, Dark Roast", "5 lb bag", (35, 48), "Bag", "Whole bean dark roast espresso blend"),
        ("Coffee", "Drip Coffee, Medium Roast", "2 lb bag", (14, 20), "Bag", "Ground medium roast coffee for brewers"),
        ("Coffee", "Decaf Coffee, Medium Roast", "2 lb bag", (15, 21), "Bag", "Ground decaffeinated medium roast coffee"),
        ("Tea", "Black Tea Bags", "box of 100", (10, 16), "Box", "Individually wrapped black tea bags"),
        ("Tea", "Green Tea Bags", "box of 100", (11, 17), "Box", "Individually wrapped green tea bags"),
        ("Tea", "Herbal Chamomile Tea Bags", "box of 100", (12, 18), "Box", "Individually wrapped caffeine-free herbal tea"),
        ("Energy/Sports", "Red Bull 8.4oz", "case of 24", (30, 38), "Case", "Energy drink, single-serve cans"),
        ("Energy/Sports", "Gatorade Fruit Punch", "case of 24", (18, 24), "Case", "Sports drink, single-serve bottles"),
        ("Milk/Dairy Bev", "Whole Milk", "half gallon", (2, 4), "Each", "Fresh whole milk for beverage service"),
        ("Milk/Dairy Bev", "Oat Milk", "32 oz carton", (4, 6), "Each", "Barista-formulated oat milk"),
        ("Milk/Dairy Bev", "Almond Milk, Unsweetened", "32 oz carton", (3, 5), "Each", "Unsweetened almond milk beverage"),
        ("Soda", "Root Beer Syrup BIB", "5 gal bag-in-box", (55, 75), "Box", "Post-mix root beer syrup concentrate"),
        ("Soda", "Club Soda Canister", "5 gal canister", (12, 18), "Box", "Carbonated water canister for soda gun"),
        ("Juice", "Grapefruit Juice", "46 oz can", (4, 6), "Each", "Canned grapefruit juice"),
        ("Juice", "Tomato Juice", "46 oz can", (3, 5), "Each", "Canned tomato juice for cocktails"),
        ("Bottled Water", "Sparkling Lemon Water 12oz", "case of 24", (15, 21), "Case", "Flavored sparkling water, lemon"),
        ("Coffee", "Cold Brew Concentrate", "gallon", (18, 26), "Gallon", "Ready-to-dilute cold brew concentrate"),
        ("Milk/Dairy Bev", "Half & Half", "quart", (3, 5), "Each", "Fresh half and half for coffee service"),
        ("Energy/Sports", "Powerade Blue", "case of 24", (16, 22), "Case", "Sports drink, single-serve bottles"),
    ],
    "Alcoholic Beverage": [
        ("Beer", "Domestic Draft Lager Keg", "1/2 barrel keg", (95, 130), "Keg", "Half-barrel keg of domestic lager"),
        ("Beer", "Craft IPA Keg", "1/6 barrel keg", (85, 115), "Keg", "Sixth-barrel keg of local craft IPA"),
        ("Beer", "Mexican Lager, Bottled", "case of 24", (30, 40), "Case", "Bottled Mexican-style lager"),
        ("Beer", "Wheat Beer, Bottled", "case of 24", (32, 42), "Case", "Bottled Belgian-style wheat beer"),
        ("Beer", "Light Lager Draft Keg", "1/2 barrel keg", (90, 120), "Keg", "Half-barrel keg of light domestic lager"),
        ("Wine", "Cabernet Sauvignon, House Red", "case of 12", (72, 96), "Case", "House-pour red wine, 750ml bottles"),
        ("Wine", "Chardonnay, House White", "case of 12", (70, 92), "Case", "House-pour white wine, 750ml bottles"),
        ("Wine", "Pinot Noir", "case of 12", (96, 132), "Case", "Mid-tier red wine, 750ml bottles"),
        ("Wine", "Sauvignon Blanc", "case of 12", (84, 108), "Case", "Mid-tier white wine, 750ml bottles"),
        ("Wine", "Prosecco", "case of 12", (90, 120), "Case", "Sparkling wine, 750ml bottles"),
        ("Wine", "Rosé", "case of 12", (78, 102), "Case", "Dry rosé wine, 750ml bottles"),
        ("Spirits", "Vodka, Well", "1.75L bottle", (18, 26), "Bottle", "Well-tier vodka for rail pours"),
        ("Spirits", "Vodka, Premium", "1L bottle", (28, 38), "Bottle", "Premium vodka for call/top-shelf pours"),
        ("Spirits", "Gin, Well", "1.75L bottle", (19, 27), "Bottle", "Well-tier London dry gin"),
        ("Spirits", "Tequila, Blanco Premium", "1L bottle", (32, 45), "Bottle", "100% agave blanco tequila"),
        ("Spirits", "Tequila, Reposado Premium", "1L bottle", (38, 52), "Bottle", "100% agave reposado tequila"),
        ("Spirits", "Bourbon, Well", "1.75L bottle", (24, 34), "Bottle", "Well-tier bourbon whiskey"),
        ("Spirits", "Bourbon, Premium", "750ml bottle", (30, 45), "Bottle", "Premium small-batch bourbon"),
        ("Spirits", "Rum, White", "1.75L bottle", (18, 26), "Bottle", "White rum for cocktails"),
        ("Spirits", "Rum, Spiced", "1L bottle", (20, 28), "Bottle", "Spiced rum for cocktails"),
        ("Spirits", "Whiskey, Rye", "750ml bottle", (26, 38), "Bottle", "Rye whiskey for classic cocktails"),
        ("Spirits", "Scotch, Blended", "750ml bottle", (28, 40), "Bottle", "Blended Scotch whisky"),
        ("Liqueur", "Triple Sec", "1L bottle", (14, 20), "Bottle", "Orange liqueur for cocktails"),
        ("Liqueur", "Coffee Liqueur", "750ml bottle", (18, 26), "Bottle", "Coffee-flavored liqueur"),
        ("Liqueur", "Amaretto", "750ml bottle", (16, 24), "Bottle", "Almond-flavored liqueur"),
        ("Beer", "Stout, Bottled", "case of 24", (34, 44), "Case", "Bottled dry Irish stout"),
        ("Beer", "Non-Alcoholic Beer", "case of 24", (28, 36), "Case", "Non-alcoholic craft-style beer"),
        ("Wine", "Champagne, Brut", "case of 6", (108, 150), "Case", "French Champagne, 750ml bottles"),
        ("Spirits", "Mezcal", "750ml bottle", (34, 48), "Bottle", "Smoky agave spirit for specialty cocktails"),
        ("Liqueur", "Vermouth, Dry", "1L bottle", (12, 18), "Bottle", "Dry vermouth for martinis"),
    ],
    "Dry Goods & Spices": [
        ("Flour", "All-Purpose Flour", "50 lb bag", (22, 30), "Bag", "Bleached all-purpose baking flour"),
        ("Flour", "Bread Flour", "50 lb bag", (24, 32), "Bag", "High-protein flour for bread and dough"),
        ("Flour", "Cornmeal", "25 lb bag", (14, 20), "Bag", "Fine yellow cornmeal"),
        ("Grain", "White Rice, Long Grain", "50 lb bag", (28, 36), "Bag", "Long grain white rice"),
        ("Grain", "Jasmine Rice", "50 lb bag", (32, 40), "Bag", "Fragrant jasmine white rice"),
        ("Grain", "Quinoa", "10 lb bag", (28, 36), "Bag", "Tri-color quinoa"),
        ("Pasta", "Spaghetti, Dry", "20 lb case", (18, 26), "Case", "Dry spaghetti pasta"),
        ("Pasta", "Penne, Dry", "20 lb case", (18, 26), "Case", "Dry penne pasta"),
        ("Legume", "Black Beans, Dry", "25 lb bag", (22, 30), "Bag", "Dried black beans"),
        ("Legume", "Pinto Beans, Dry", "25 lb bag", (20, 28), "Bag", "Dried pinto beans"),
        ("Sugar", "Granulated Sugar", "50 lb bag", (24, 32), "Bag", "Granulated white cane sugar"),
        ("Sugar", "Brown Sugar", "25 lb bag", (16, 22), "Bag", "Light brown sugar"),
        ("Sugar", "Powdered Sugar", "25 lb bag", (16, 22), "Bag", "Confectioners' powdered sugar"),
        ("Spice", "Kosher Salt", "25 lb bag", (10, 16), "Bag", "Coarse kosher salt"),
        ("Spice", "Black Pepper, Ground", "1 lb bag", (8, 14), "Bag", "Finely ground black pepper"),
        ("Spice", "Paprika, Smoked", "1 lb bag", (9, 15), "Bag", "Smoked Spanish paprika"),
        ("Spice", "Cumin, Ground", "1 lb bag", (8, 14), "Bag", "Ground cumin seed"),
        ("Spice", "Chili Powder", "1 lb bag", (7, 13), "Bag", "Blended chili powder"),
        ("Spice", "Garlic Powder", "1 lb bag", (7, 12), "Bag", "Dehydrated garlic powder"),
        ("Spice", "Onion Powder", "1 lb bag", (6, 11), "Bag", "Dehydrated onion powder"),
        ("Spice", "Cayenne Pepper", "1 lb bag", (8, 13), "Bag", "Ground cayenne pepper"),
        ("Spice", "Oregano, Dried", "1 lb bag", (10, 16), "Bag", "Dried oregano leaves"),
        ("Spice", "Cinnamon, Ground", "1 lb bag", (9, 15), "Bag", "Ground Ceylon cinnamon"),
        ("Baking", "Baking Powder", "10 lb can", (18, 26), "Each", "Double-acting baking powder"),
        ("Baking", "Baking Soda", "12 lb box", (10, 16), "Box", "Sodium bicarbonate baking soda"),
        ("Baking", "Cocoa Powder", "5 lb bag", (18, 26), "Bag", "Unsweetened dark cocoa powder"),
        ("Breading", "Panko Bread Crumbs", "25 lb case", (28, 38), "Case", "Japanese-style panko breadcrumbs"),
        ("Breading", "Seasoned Bread Crumbs", "25 lb case", (26, 36), "Case", "Pre-seasoned breadcrumb coating"),
        ("Nuts/Seeds", "Sesame Seeds", "5 lb bag", (18, 26), "Bag", "Hulled white sesame seeds"),
        ("Nuts/Seeds", "Sliced Almonds", "5 lb bag", (24, 32), "Bag", "Blanched sliced almonds"),
    ],
    "Frozen/Refrigerated Goods": [
        ("Frozen Vegetable", "Frozen Peas", "20 lb case", (24, 32), "Case", "IQF frozen green peas"),
        ("Frozen Vegetable", "Frozen Corn", "20 lb case", (22, 30), "Case", "IQF frozen sweet corn"),
        ("Frozen Vegetable", "Frozen Broccoli Florets", "20 lb case", (26, 34), "Case", "IQF frozen broccoli florets"),
        ("Frozen Vegetable", "Frozen Spinach, Chopped", "20 lb case", (22, 30), "Case", "IQF frozen chopped spinach"),
        ("Frozen Potato", "French Fries, Straight Cut", "30 lb case", (26, 34), "Case", "Frozen par-fried straight-cut fries"),
        ("Frozen Potato", "Tater Tots", "30 lb case", (28, 36), "Case", "Frozen potato tots"),
        ("Frozen Potato", "Hash Browns, Shredded", "20 lb case", (22, 30), "Case", "Frozen shredded hash browns"),
        ("Frozen Bread", "Dinner Rolls, Par-Baked", "case of 200", (34, 44), "Case", "Frozen par-baked dinner rolls"),
        ("Frozen Bread", "Pizza Dough Balls", "case of 40", (36, 48), "Case", "Frozen pre-portioned pizza dough"),
        ("Frozen Dessert", "Vanilla Ice Cream", "3 gal tub", (24, 32), "Each", "Vanilla ice cream, foodservice tub"),
        ("Frozen Dessert", "Chocolate Ice Cream", "3 gal tub", (24, 32), "Each", "Chocolate ice cream, foodservice tub"),
        ("Frozen Dessert", "Cheesecake, Uncut", "10 inch", (18, 26), "Each", "Frozen uncut New York cheesecake"),
        ("Frozen Fruit", "Frozen Mixed Berries", "10 lb bag", (28, 38), "Bag", "IQF mixed berries for desserts and smoothies"),
        ("Frozen Fruit", "Frozen Mango Chunks", "10 lb bag", (24, 32), "Bag", "IQF mango chunks"),
        ("Dairy", "Shredded Mozzarella", "5 lb bag", (18, 26), "Bag", "Low-moisture shredded mozzarella"),
        ("Dairy", "Shredded Cheddar", "5 lb bag", (18, 26), "Bag", "Sharp shredded cheddar cheese"),
        ("Dairy", "Parmesan, Grated", "5 lb bag", (28, 38), "Bag", "Grated parmesan cheese"),
        ("Dairy", "Cream Cheese", "3 lb block", (10, 15), "Each", "Foodservice block cream cheese"),
        ("Dairy", "Butter, Unsalted", "36 lb case", (110, 150), "Case", "Unsalted butter, 1 lb blocks"),
        ("Dairy", "Heavy Cream", "quart", (4, 6), "Each", "Fresh heavy whipping cream"),
        ("Dairy", "Sour Cream", "5 lb tub", (12, 18), "Each", "Cultured sour cream"),
        ("Dairy", "Eggs, Large", "case of 15 dz", (48, 68), "Case", "Grade A large eggs"),
        ("Frozen Protein", "Frozen Shrimp, 21/25", "5 lb bag", (48, 65), "Bag", "IQF peeled deveined shrimp"),
        ("Frozen Protein", "Frozen Chicken Wings", "40 lb case", (85, 115), "Case", "Frozen bone-in chicken wings"),
        ("Frozen Protein", "Frozen Salmon Fillets", "10 lb box", (75, 100), "Box", "IQF skin-on salmon fillets"),
        ("Frozen Appetizer", "Mozzarella Sticks", "case of 240", (55, 72), "Case", "Breaded frozen mozzarella sticks"),
        ("Frozen Appetizer", "Spring Rolls, Vegetable", "case of 100", (48, 62), "Case", "Frozen vegetable spring rolls"),
        ("Dairy", "Yogurt, Plain", "5 lb tub", (14, 20), "Each", "Plain whole milk yogurt"),
        ("Frozen Vegetable", "Frozen Diced Onions", "20 lb case", (20, 28), "Case", "IQF diced yellow onions"),
        ("Frozen Dessert", "Pie Crust, Frozen 9in", "case of 24", (30, 40), "Case", "Frozen unbaked pie shells"),
    ],
    "Liquids/Pastes/Sauces": [
        ("Oil", "Canola Oil", "35 lb jug", (38, 50), "Jug", "Refined canola frying/cooking oil"),
        ("Oil", "Olive Oil, Extra Virgin", "3 L tin", (24, 34), "Each", "Extra virgin olive oil for finishing"),
        ("Oil", "Vegetable Oil", "35 lb jug", (36, 46), "Jug", "Blended vegetable frying oil"),
        ("Oil", "Sesame Oil", "1 gal jug", (26, 36), "Gallon", "Toasted sesame oil for flavoring"),
        ("Vinegar", "White Vinegar", "1 gal jug", (6, 10), "Gallon", "Distilled white vinegar"),
        ("Vinegar", "Balsamic Vinegar", "1 gal jug", (22, 32), "Gallon", "Aged balsamic vinegar"),
        ("Vinegar", "Rice Wine Vinegar", "1 gal jug", (14, 20), "Gallon", "Seasoned rice wine vinegar"),
        ("Sauce", "Soy Sauce", "1 gal jug", (12, 18), "Gallon", "Traditional brewed soy sauce"),
        ("Sauce", "Hot Sauce", "1 gal jug", (16, 24), "Gallon", "Cayenne pepper hot sauce"),
        ("Sauce", "Worcestershire Sauce", "1 gal jug", (14, 20), "Gallon", "Fermented Worcestershire sauce"),
        ("Sauce", "BBQ Sauce", "1 gal jug", (14, 20), "Gallon", "Sweet and smoky barbecue sauce"),
        ("Sauce", "Buffalo Wing Sauce", "1 gal jug", (16, 22), "Gallon", "Buffalo-style hot wing sauce"),
        ("Sauce", "Teriyaki Sauce", "1 gal jug", (14, 20), "Gallon", "Sweet soy teriyaki sauce"),
        ("Sauce", "Ranch Dressing", "1 gal jug", (16, 22), "Gallon", "Creamy ranch salad dressing"),
        ("Sauce", "Caesar Dressing", "1 gal jug", (18, 24), "Gallon", "Creamy Caesar salad dressing"),
        ("Sauce", "Vinaigrette, Balsamic", "1 gal jug", (16, 22), "Gallon", "Balsamic vinaigrette dressing"),
        ("Paste", "Tomato Paste", "#10 can", (8, 13), "Each", "Double-concentrated tomato paste"),
        ("Paste", "Garlic Paste", "4 lb tub", (14, 20), "Each", "Minced garlic in oil paste"),
        ("Paste", "Ginger Paste", "4 lb tub", (14, 20), "Each", "Minced ginger paste"),
        ("Paste", "Curry Paste, Red", "14 oz can", (5, 8), "Each", "Thai red curry paste"),
        ("Canned Tomato", "Crushed Tomatoes", "#10 can", (7, 11), "Each", "Crushed tomatoes in puree"),
        ("Canned Tomato", "Diced Tomatoes", "#10 can", (7, 11), "Each", "Diced tomatoes in juice"),
        ("Canned Tomato", "Tomato Puree", "#10 can", (7, 11), "Each", "Smooth tomato puree"),
        ("Stock/Broth", "Chicken Stock, Liquid", "1 gal jug", (12, 18), "Gallon", "Ready-to-use liquid chicken stock"),
        ("Stock/Broth", "Beef Stock, Liquid", "1 gal jug", (14, 20), "Gallon", "Ready-to-use liquid beef stock"),
        ("Stock/Broth", "Vegetable Stock, Liquid", "1 gal jug", (12, 18), "Gallon", "Ready-to-use liquid vegetable stock"),
        ("Sauce", "Marinara Sauce", "#10 can", (10, 15), "Each", "Prepared marinara pasta sauce"),
        ("Sauce", "Alfredo Sauce", "4 lb tub", (14, 20), "Each", "Prepared creamy alfredo sauce"),
        ("Sauce", "Sriracha", "1 gal jug", (18, 26), "Gallon", "Sweet chili garlic hot sauce"),
        ("Honey/Syrup", "Honey", "5 lb jug", (18, 26), "Each", "Pure clover honey"),
    ],
    "Produce & Meat": [
        ("Produce", "Romaine Lettuce", "case of 24 heads", (28, 38), "Case", "Fresh romaine lettuce heads"),
        ("Produce", "Iceberg Lettuce", "case of 24 heads", (24, 32), "Case", "Fresh iceberg lettuce heads"),
        ("Produce", "Tomatoes, Roma", "25 lb case", (28, 40), "Case", "Fresh Roma tomatoes"),
        ("Produce", "Onions, Yellow", "50 lb bag", (22, 32), "Bag", "Fresh yellow cooking onions"),
        ("Produce", "Garlic, Fresh", "10 lb case", (28, 38), "Case", "Fresh whole garlic bulbs"),
        ("Produce", "Bell Peppers, Green", "25 lb case", (30, 42), "Case", "Fresh green bell peppers"),
        ("Produce", "Bell Peppers, Red", "25 lb case", (36, 48), "Case", "Fresh red bell peppers"),
        ("Produce", "Avocados", "case of 48", (48, 68), "Case", "Fresh Hass avocados"),
        ("Produce", "Limes", "case of 200", (30, 42), "Case", "Fresh limes"),
        ("Produce", "Lemons", "case of 165", (32, 44), "Case", "Fresh lemons"),
        ("Produce", "Potatoes, Russet", "50 lb bag", (24, 34), "Bag", "Fresh russet potatoes"),
        ("Produce", "Carrots", "25 lb bag", (18, 26), "Bag", "Fresh whole carrots"),
        ("Produce", "Celery", "case of 30", (24, 32), "Case", "Fresh celery stalks"),
        ("Produce", "Mushrooms, White Button", "10 lb case", (26, 36), "Case", "Fresh white button mushrooms"),
        ("Produce", "Cilantro", "case of 30 bunches", (18, 26), "Case", "Fresh cilantro bunches"),
        ("Produce", "Jalapeños", "10 lb case", (16, 24), "Case", "Fresh jalapeño peppers"),
        ("Produce", "Cucumbers", "case of 24", (18, 26), "Case", "Fresh cucumbers"),
        ("Produce", "Spinach, Fresh", "4 lb case", (14, 20), "Case", "Fresh baby spinach"),
        ("Produce", "Basil, Fresh", "case of 12 bunches", (22, 30), "Case", "Fresh basil bunches"),
        ("Produce", "Ginger, Fresh", "10 lb case", (28, 38), "Case", "Fresh ginger root"),
        ("Meat", "Ground Beef, 80/20", "case", (4, 6), "Lb", "Fresh ground beef, 80/20 blend"),
        ("Meat", "Chicken Breast, Boneless", "case", (3, 5), "Lb", "Fresh boneless skinless chicken breast"),
        ("Meat", "Chicken Thighs, Boneless", "case", (2, 4), "Lb", "Fresh boneless skinless chicken thighs"),
        ("Meat", "Pork Shoulder", "case", (3, 5), "Lb", "Fresh bone-in pork shoulder"),
        ("Meat", "Bacon, Sliced", "15 lb case", (55, 75), "Case", "Sliced smoked bacon"),
        ("Meat", "NY Strip Steak", "case", (12, 18), "Lb", "Fresh NY strip steak, portioned"),
        ("Meat", "Ribeye Steak", "case", (14, 20), "Lb", "Fresh ribeye steak, portioned"),
        ("Meat", "Ground Pork", "case", (3, 5), "Lb", "Fresh ground pork"),
        ("Seafood", "Salmon Fillet, Fresh", "case", (10, 15), "Lb", "Fresh Atlantic salmon fillet"),
        ("Seafood", "Shrimp, Fresh 16/20", "case", (11, 16), "Lb", "Fresh peeled deveined shrimp"),
    ],
    "Supplies": [
        ("To-Go", "To-Go Containers, 32oz", "case of 150", (30, 42), "Case", "Clamshell to-go containers"),
        ("To-Go", "To-Go Cups, 16oz", "case of 1000", (55, 75), "Case", "Cold cup to-go beverage cups"),
        ("To-Go", "To-Go Cup Lids, Dome", "case of 1000", (28, 38), "Case", "Dome lids for cold cups"),
        ("To-Go", "Paper Bags, Kraft", "case of 500", (32, 44), "Case", "Kraft paper takeout bags"),
        ("Disposable", "Napkins, Dinner", "case of 3000", (28, 38), "Case", "1-ply dinner napkins"),
        ("Disposable", "Straws, Wrapped", "box of 500", (8, 14), "Box", "Individually wrapped plastic straws"),
        ("Disposable", "Plastic Cutlery, Forks", "box of 1000", (14, 20), "Box", "Disposable plastic forks"),
        ("Disposable", "Plastic Cutlery, Spoons", "box of 1000", (14, 20), "Box", "Disposable plastic spoons"),
        ("Disposable", "Toothpicks", "box of 1000", (4, 7), "Box", "Wooden toothpicks"),
        ("Cleaning", "Dish Soap, Concentrate", "1 gal jug", (18, 26), "Gallon", "Commercial dish soap concentrate"),
        ("Cleaning", "Degreaser, Kitchen", "1 gal jug", (16, 24), "Gallon", "Heavy-duty kitchen degreaser"),
        ("Cleaning", "Sanitizer Solution", "1 gal jug", (14, 20), "Gallon", "Food-safe sanitizing solution"),
        ("Cleaning", "Bleach", "1 gal jug", (5, 9), "Gallon", "Standard cleaning bleach"),
        ("Cleaning", "Glass Cleaner", "1 gal jug", (12, 18), "Gallon", "Streak-free glass cleaner"),
        ("Paper Goods", "Paper Towels, Roll", "case of 12", (32, 44), "Case", "Commercial roll paper towels"),
        ("Paper Goods", "Toilet Paper, Roll", "case of 48", (36, 48), "Case", "Commercial roll toilet paper"),
        ("Paper Goods", "Butcher Paper Roll", "roll", (24, 34), "Roll", "Food-grade butcher paper roll"),
        ("Paper Goods", "Parchment Paper Sheets", "box of 1000", (38, 50), "Box", "Pre-cut parchment paper sheets"),
        ("Wrap/Film", "Plastic Wrap Roll", "roll", (18, 26), "Roll", "Commercial food-service plastic wrap"),
        ("Wrap/Film", "Aluminum Foil Roll", "roll", (22, 32), "Roll", "Heavy-duty aluminum foil roll"),
        ("Gloves", "Disposable Gloves, Nitrile", "case of 1000", (45, 60), "Case", "Powder-free nitrile gloves"),
        ("Gloves", "Disposable Gloves, Vinyl", "case of 1000", (32, 44), "Case", "Powder-free vinyl gloves"),
        ("Storage", "Food Storage Containers", "case of 100", (36, 48), "Case", "Clear polycarbonate storage containers"),
        ("Storage", "Container Lids", "case of 100", (18, 26), "Case", "Lids for storage containers"),
        ("Storage", "Deli Cups w/ Lids, 8oz", "case of 500", (32, 44), "Case", "Clear deli portion cups with lids"),
        ("Chemical", "Hand Soap", "1 gal jug", (12, 18), "Gallon", "Foodservice hand soap"),
        ("Chemical", "Hand Sanitizer", "1 gal jug", (16, 24), "Gallon", "Alcohol-based hand sanitizer"),
        ("Small Wares", "Chafing Fuel Cans", "case of 24", (30, 42), "Case", "Gel fuel cans for chafing dishes"),
        ("Small Wares", "Aluminum Steam Table Pans", "case of 50", (48, 65), "Case", "Full-size disposable steam table pans"),
        ("Menu/Marketing", "Menu Paper, Cardstock", "ream of 500", (18, 26), "Each", "Cardstock paper for printed menus"),
    ],
}

CATEGORY_PREFIX = {
    "Non-Alcoholic Beverage": "NAB",
    "Alcoholic Beverage": "ALC",
    "Dry Goods & Spices": "DRY",
    "Frozen/Refrigerated Goods": "FRZ",
    "Liquids/Pastes/Sauces": "LIQ",
    "Produce & Meat": "PRD",
    "Supplies": "SUP",
}


def generate_rows():
    rows = []
    for category, items in PRODUCTS.items():
        prefix = CATEGORY_PREFIX[category]
        for i, (subcat, name, uom, price_range, _pack_method, desc) in enumerate(items, start=1):
            primary_key = f"{prefix}-{i:03d}"
            wholesale_price = round(random.uniform(*price_range), 2)
            primary_vendor, secondary_vendor = random.sample(VENDORS, 2)
            buy_method = random.choice(BUY_METHODS)

            rows.append({
                "Category": category,
                "Subcategory": subcat,
                "Primary Key": primary_key,
                "Item Name": name,
                "Unit of Measure": uom,
                "Wholesale Price": wholesale_price,
                "Primary Vendor": primary_vendor,
                "Secondary Vendor": secondary_vendor,
                "Buy Method": buy_method,
                "Description": desc,
            })
    return rows


def main(output_path="master_product_list.csv"):
    rows = generate_rows()
    fieldnames = [
        "Category", "Subcategory", "Primary Key", "Item Name",
        "Unit of Measure", "Wholesale Price", "Primary Vendor",
        "Secondary Vendor", "Buy Method", "Description",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows across {len(PRODUCTS)} categories -> {output_path}")


if __name__ == "__main__":
    main()
