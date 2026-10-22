---
name: transaction-category
description: "Map one statement line to a Family Book category using the learned merchant map, merchant patterns, and the issuer spend category. Ask once for an unknown big charge."
---

# Transaction category

Map one normalized statement line to one book category. The expense-category skill is for receipt items. This skill is for the statement line when no receipt is splitting it.

Look up in this order. The first hit wins.

1. **Learned map**, sheet `Merchant Map` (hidden). The pattern is the leading merchant words, lowercased, with a store number removed and with the city in front of a province removed. `ACME WIDGETS PORTLAND OR` is stored as `acme widgets`. If that pattern is contained in the new description, use the stored category and do not ask again.
2. **Merchant patterns** below. These override the issuer's spend category. Shell is Fuel even when CIBC prints Transportation.
3. **Issuer spend category**, when the statement prints one and no pattern hit.
4. **Unknown.** If the absolute amount is at least 75 in the book currency, ask once and write nothing in the grid until the user answers. Then add the pattern to `Merchant Map` with Source `learned` and Confirmed `yes`. If the amount is under 75, use Other and do not ask.

The default 75 can be changed from memory (`big_charge_threshold`). A question row holds no grid amount. The Transactions row may show the amount with Status `question`, because that section is not in the totals. Where written stays blank until the user answers.

## Merchant patterns

| Description contains | Category |
|---|---|
| ANNUAL RENEWAL | Other |
| ANNUAL FEE, INTEREST CHARGE, CASH ADVANCE FEE | Bank fees |
| SHELL, PETRO-CANADA, ESSO, GASBAR, GAS BAR | Fuel |
| TIM HORTONS, STARBUCKS | Snacks |
| MCDONALDS, A&W, SUBWAY, WENDYS | Dining Out |
| NETFLIX, SPOTIFY, DISNEY, CINEPLEX | Entertainment |
| PROPERTY TAX, or a merchant that ends in TAX (OAKVILLE-TAX) | Property Tax |
| SPORT CHEK, OLD NAVY, WINNERS | Clothing |
| HOME DEPOT, CANADIAN TIRE (not the gas bar), RONA, IKEA | Household Goods |
| SHOPPERS, PHARMACY, DENTAL, a line starting with DR | Medical |
| COSTCO, WALMART, T&T, WHOLE FOODS, SUPERMARKET, FOODMART, LOBLAW, NO FRILLS, GROCERY | Snacks |
| PRESTO, UBER, LYFT, PARKING | Transportation |
| MORTGAGE | Rent / Mortgage |
| HYDRO, ENBRIDGE, ELECTRIC | Electricity & Water |
| COGECO, BELL internet, ROGERS internet | Internet |

Tim Hortons and coffee shops are Snacks. McDonalds, A&W, and Subway are Dining Out. Those are the food categories a statement line can land in when there is no receipt. A receipt's own items can still split into Meals.

Property Tax, Rent / Mortgage, GAS, Electricity & Water, Internet, and the other Fixed Expenses labels go to Fixed Expenses This Month (column C of that row), not the daily grid. Bank fees is the category name, and the amount is written on Other (rows 37-40) because the number grid does not gain a new row.

## Issuer spend category, when no pattern hit

| Printed by the issuer | Book category |
|---|---|
| Transportation | Transportation |
| Restaurants | Dining Out |
| Retail and Grocery | Snacks |
| Personal and Household Expenses | Household Goods |
| Hotel, Entertainment and Recreation | Entertainment |
| Health and Education | Medical |
| Professional and Financial Services | Bank fees |
| Home and Office Improvement | Household Goods |
| Other Transactions | Other |

## Where the amount goes

Daily categories use the v1.2.4 blocks: Meals 6-16, Snacks 17-19, Dining Out 20, Household Goods 22-27, Education 28, Fuel 29, Clothing 30-31, Medical 32, Hair & Cosmetics 33, Transportation 34, Entertainment 35, Gifts & Social 36, Other 37-40, Temporary Income 43. The day comes from the transaction date. Day 1 amount is column K, day 31 is column BS. The first empty amount cell in the block is the cell. Record it on the Log before writing. If the block is full, fold into the last cell as one formula, once. A retry uses the recorded cell.
