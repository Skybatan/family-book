---
name: expense-category
description: "Sort receipt line items into Family Book categories and split one receipt so the parts add up to the total. Extends the v1.2.4 item rules."
---

# Expense category

Use this for the items on a receipt. A statement line with no receipt uses the transaction-category skill for the whole amount instead.

The book categories are the daily rows: Meals, Snacks, Dining Out, Household Goods, Education & Enrichment, Fuel, Clothing, Medical, Hair & Cosmetics, Transportation, Entertainment, Gifts & Social, Other, and Temporary Income for a refund that is new money. Fixed bills (rent, hydro, insurance, property tax) stay in Fixed Expenses and are not split across items.

## Item patterns

| Item text | Category |
|---|---|
| tip, gratuity | Dining Out |
| egg, milk, bread, chicken, beef, meat, fish, seafood, vegetable, produce, banana, grocery | Meals |
| chip, candy, snack, cookie, coffee, pop, soda | Snacks |
| paper, towel, detergent, cleaner, soap, paint, brush, tool, battery | Household Goods |
| jacket, shirt, shoe, adidas, clothing | Clothing |
| gas, fuel, unleaded | Fuel |
| pharmacy, vitamin, prescription | Medical |
| ticket, movie | Entertainment |
| anything else | Other |

One purchase still uses one receipt row. Each item keeps its own category in the Receipts section (`Item n`, `Price`, `Category`). On the grid, items that share a category are one amount: the sum of those items. Tax, a discount, or a fee that is not its own item is spread in proportion to the item prices so the category amounts add up to the receipt total to the cent. Put a leftover cent on the largest item.

Example: eggs 18.00 (Meals), chicken 20.00 (Meals), paper towel 42.00 (Household Goods), total 80.00. The grid gets Meals 38.00 and Household Goods 42.00. The Receipts section still lists the three items.

A tip printed as its own item is Dining Out. A tip that is only the gap between the receipt total and the statement amount is not categorized here. The receipt-match skill asks before linking that pair.

Write the short product name in the language of the chat. The column headers stay English.
