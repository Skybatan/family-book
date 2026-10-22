---
name: expense-category
description: "Sort receipt line items into Family Book categories and split one receipt so the parts add up to the total. Extends the v1.2.4 item rules."
---

# Expense category

Use this for the items on a receipt. A statement line with no receipt uses the transaction-category skill for the whole amount instead.

The book categories are the daily rows: Meals, Snacks, Dining Out, Household Goods, Education & Enrichment, Fuel, Clothing, Medical, Hair & Cosmetics, Transportation, Entertainment, Gifts & Social, Other, and Temporary Income for a refund that is new money. Fixed bills (rent, hydro, insurance, property tax) stay in Fixed Expenses and are not split across items.

Categorize each item by what it is. The words below are examples, not the whole list. A printed name that is not in the table still gets the category its meaning belongs to.

## Examples

| What it is | Examples | Category |
|---|---|---|
| A tip | tip, gratuity | Dining Out |
| Food for home cooking | egg, milk, bread, chicken, beef, meat, fish, salmon, tuna, shrimp, seafood, vegetable, spinach, lettuce, tomato, onion, carrot, broccoli, produce, banana, grocery | Meals |
| A snack or a drink | chip, candy, snack, cookie, coffee, pop, soda | Snacks |
| Household goods or home repair | paper, towel, detergent, cleaner, soap, paint, brush, tool, battery, drywall screws, drop cloth | Household Goods |
| Clothing | jacket, shirt, shoe, adidas, clothing | Clothing |
| Pump fuel written as a grade and a volume | Regular 38.31L | Transportation |
| Other fuel | gas, fuel, unleaded | Fuel |
| Medical | pharmacy, vitamin, prescription | Medical |
| Entertainment | ticket, movie | Entertainment |
| None of these | | Other |

Salmon and spinach are Meals. `Regular 38.31L` is Transportation. Drywall screws and a drop cloth are Household Goods. Use these template names, not a separate "home repair" label.

One purchase still uses one receipt row. Each item keeps its own category in the Receipts section (`Item n`, `Price`, `Category`). On the grid, items that share a category are one amount: the sum of those items. Tax, a discount, or a fee that is not its own item is spread in proportion to the item prices so the category amounts add up to the receipt total to the cent. Put a leftover cent on the largest item.

Example: eggs 18.00 (Meals), chicken 20.00 (Meals), paper towel 42.00 (Household Goods), total 80.00. The grid gets Meals 38.00 and Household Goods 42.00. The Receipts section still lists the three items.

A tip printed as its own item is Dining Out. A tip that is only the gap between the receipt total and the statement amount is not categorized here. The receipt-match skill asks before linking that pair.

Write the short product name in the language of the chat. The column headers stay English.
