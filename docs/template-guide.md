# Family Book Template Guide

An Excel workbook for tracking a family's income and spending, month by month, with an automatic yearly summary.
The template is [`template/family-book-template.xlsx`](../template/family-book-template.xlsx). It is completely empty: all labels and formulas are in place, and no year or dates show until the year is set.

If you use Family Book with Grok Bot, the bot creates each year's book for you with the year, currency, and public holidays already filled in, and logs your receipts. You can skip straight to [Workbook layout](#workbook-layout) to see where things go. If you use the template by hand, follow [Getting started](#getting-started).

Adapted from a Microsoft Template Center template (original author: Antony Liaw). Currency in the template is CAD. With Grok Bot, your currency is applied at setup; by hand, change the number format if you use another currency.

## How it works

```mermaid
flowchart LR
    Y[Annual Summary: the year] --> M[Month sheets Jan-Dec]
    H[Holidays: optional dates] --> M
    M -->|income, fixed bills, daily spending| A[Annual Summary: totals, shares, net]
```

Entries go into the **month sheets**; the year is set once per book (by the bot, or by you if you use the template by hand). Everything on the **Annual Summary** is calculated.

## Workbook layout

| Sheet | Purpose | You type here? |
|---|---|---|
| Annual Summary | Year, monthly balance, expenses by category, share of expenses, net | Only the year (`F5`), and only by hand; the bot fills it in |
| Jan ... Dec | One sheet per month: income, fixed expenses, daily spending | Yes |
| Holidays | Optional public holidays, company holidays and anniversaries, shown on the matching day in each month | Optional |

## Getting started

**With Grok Bot:** nothing to do here. The bot copies the template, sets the year in `F5`, applies your currency, and fills in your public holidays. See the [setup guide](setup-guide.md).

**By hand:**

1. Copy the template and rename it (for example `Family Book 2026.xlsx`).
2. On **Annual Summary**, enter the year in `F5` (it starts empty). Every month sheet takes its dates from this cell, so the day headers stay blank until the year is set.
3. Fill in each month sheet as described below.
4. Read the totals on **Annual Summary**.

Light grey cells are formulas; do not overwrite them. Use the "Back to Annual Summary" link at the top of a sheet to navigate, and the month names on Annual Summary to jump to a month.

## Filling in a month sheet

### 1. Income This Month (left, top)

Enter each income source in a row: **Item**, **Amount**, **Date Received** (up to 4 rows). *Total Income* is calculated.

### 2. Fixed Expenses This Month (left, bottom)

Recurring bills. Enter the **Amount** and **Date Paid** next to the pre-set item:

| Item | Notes |
|---|---|
| Income | Enter as a **negative** number. It is treated as an offset (for example rental income) and is excluded from *Total Expenses* on Annual Summary |
| GAS, Electricity & Water, RESP, Mobile Phone, Daycare | |
| Rent / Mortgage, Internet, Car Insurance, Property Tax | |
| Fuel / Maintenance, Home Insurance, Car Loan Payment | |
| Housing Management Fee, Term Deposit, Pocket Money, Savings | Counted in the monthly balance, but **not** in the Annual Summary category table |

Rename or reuse items to suit your family; keep each amount in the same row so the Annual Summary links stay correct.

### 3. Daily Record (right)

Each day has two columns: **Item** (what/where) and **Amount**. Put each purchase in the row of its category. Weekends are highlighted, and holidays/anniversaries from the Holidays sheet appear at the top of the day.

### 4. Results (middle)

*Living Expenses This Month*, *Balance This Month* and *Cumulative Balance* are calculated:

```text
Balance This Month = Total Income - Total Fixed Expenses - Total Living Expenses + Temporary Income
Cumulative Balance = this month's balance + previous month's cumulative balance
```

*Temporary Income* (row 43) is one-off money received on a given day (a refund, cash back, a sold item). *Notes This Month* is free text.

## How expenses are categorised

Place each daily purchase in the row for its category. These rows feed the Annual Summary.

| Category (daily rows) | Rows | Annual Summary line |
|---|---|---|
| Meals (staple foods and side dishes for home cooking) | 6-16 | Food (Meals) |
| Dining Out (restaurants, takeout) | 20 | Food (Meals) |
| Snacks & Groceries (snacks and general grocery-store trips) | 17-19 | Snacks & Groceries |
| Household Goods | 22-27 | Household Goods |
| Education & Enrichment (lessons, classes, books) | 28 | Education & Enrichment |
| Fuel | 29 | Fuel |
| Clothing | 30-31 | Clothing |
| Medical | 32 | Medical |
| Hair & Cosmetics | 33 | Hair & Cosmetics |
| Transportation (transit, parking, tolls) | 34 | Transportation |
| Entertainment (subscriptions, movies, outings) | 35 | Entertainment |
| Gifts & Social | 36 | Gifts & Social |
| Other | 37-40 | Other |

Rules of thumb:

- **Pick one category per purchase.** Do not enter the same amount twice. If a receipt spans categories (for example one store trip with food and household items), split it into separate entries, one per category.
- **Row 41 is not part of the Annual Summary categories.** Use rows 37-40 for "Other".
- A row can hold several entries on the same day by typing a sum in the Amount cell, for example `=12.50+8.20`.
- A refund can be entered as a negative amount in the same category.
- Row 21 (*Total Food*), row 42 (*Daily Expenses Total*) and row 44 (*Balance*) are calculated; do not type there.

Fixed expenses (rent, insurance, loan, utilities) are entered once per month in the left-hand list, not in the daily record.

## Reading the Annual Summary

- **Monthly Totals / Monthly Balance:** each month's remaining balance, and the year total.
- **Expenses by Category:** every category by month, with the **Annual Total** and **Share of Expenses** (each category's share of all expenses).
- **Total Expenses** = all category lines except the *Income* line. **Net** = Total Expenses + Income (income entered as negative lowers spending).

## Tips

- Enter spending daily or weekly; keep a consistent naming style for items (for example `Costco`, not `COSTCO` and `costco`) so you can scan the record later.
- Leave days that do not exist in a month (such as the 31st of a 30-day month) blank; they stay empty automatically.
- **Holidays sheet:** the year in each date must match the year, otherwise it will not show. Leave unused cells empty.
- **Google Sheets:** the file can be imported (Drive > open with Google Sheets). Formulas work, but click-test the navigation links, and set the sheet locale so weekday names display correctly.
- Make a fresh copy of the template each year rather than overwriting an old year (Grok Bot does this for you each December).
