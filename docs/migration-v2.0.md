# Migration to Family Book v2.0

v2.0 adds a Transactions section and a Receipts section on each month sheet, a Cards sheet, a merchant map, and statement import. The number grid on top of each month does not change. The bot follows [bot/skills/family-book-migrate/SKILL.md](../bot/skills/family-book-migrate/SKILL.md). This page is the plan for people.

Annual Summary cell `C46` is the marker.

| `C46` | What happens |
|---|---|
| `v2.0` | The book is current. Nothing is rebuilt. |
| `v1.2.4` | Receipt rows are copied into the Receipts section. Totals stay as they are. |
| `v1.2.3` or older | The book first picks up the [v1.2.4 checkpoint](migration-v1.2.4.md), then the v2.0 copy. The bot does not stop at v1.2.4. |
| `migrating` | A previous run stopped. The next run continues and does not add a second copy of a row. |

## What stays

Income, fixed bills, and daily amounts are not retyped. A receipt that was already in the grid stays in those cells. The migration does not add the amount again.

## What is added

- **Transactions this month**, then **Receipts this month**, under the totals. Old receipt-list rows become Receipts rows: receipt number, store, date, total, card, items, and the file link.
- A **Cards** sheet (issuer, product, last 4, holder, statement day, due day, last amount due, paid status). It starts empty until you name a card or import a statement.
- A hidden **Merchant Map** and a hidden **Statements** sheet. The bot asks once if it cannot hide a tab, and it keeps going.
- A `statements` folder: `Family Book - {year}/statements/{Issuer Product}-{last4}/`.

## Duplicates

A duplicate pair stays as two rows. The bot writes it into `D46` and asks. It does not delete a row. A yes clears only the extra amount. A no leaves both amounts.

## The first statement after the update

A statement line that matches a Receipts row is linked. The amount is not added again. A statement line with no receipt is new, and it fills the grid once. Importing that same statement again adds nothing.

## Run it twice

The owner's bot runs this once, for every year in the `Family Book` folder. A second run copies nothing. A family member's bot does not run it.

Made by SkybatanX (@SkyXFunNext).
