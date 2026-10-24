# Migration to Family Book v2.1

v2.1 does not rebuild a book. A book that is already v2.0 keeps every amount, every formula, and every receipt and transaction row. The owner's bot writes a few settings cells and sets Annual Summary `C46` to `v2.1`. The bot follows the "Continue to v2.1" section of [bot/skills/family-book-migrate/SKILL.md](../bot/skills/family-book-migrate/SKILL.md). It is safe to run twice. A second run changes nothing.

Books older than v2.0 still follow [migration-v2.0.md](migration-v2.0.md) first. The same run then does this settings step. It does not stop at `v2.0`.

## Cells

| Cell | Label | Value |
|---|---|---|
| `C46` | Book version | `v2.1` |
| `B47` | Statement features | label only |
| `C47` | | `off` or `on` |
| `B48` | Statement offer | label only |
| `C48` | | `not yet`, `asked`, `declined`, or `accepted` |
| `B49`–`B51` | Last weekly / monthly / yearly report | labels; the date cells start blank |
| `B52` | Book started | label |
| `C52` | | today's date when it was blank. This is not a receipt date |

`C47` is filled only when it is blank.

- `on` when the book already has a Statements row, a Transactions row, or a Cards row with a last 4. Reminders that were already in use stay on.
- `off` when those sections are empty. The book is receipts-only until a statement is added.

`C48` is filled only when it is blank: `accepted` if features are on, otherwise `not yet`. A `declined` or `asked` value is left as it is, so a no is not forgotten and the question is not asked again. `B48` is still set to `Statement offer` when that label is missing, even if `C48` already says `declined`. A statement the user imports later can change `declined` to `accepted`. This step does not.

The banner in `B2` changes only the version token, from `Family Book v2.0` to `Family Book v2.1`, when that is how the banner starts. The rest of the banner stays.

## What does not change

Income, fixed bills, daily amounts, receipt totals, and transaction amounts are not edited. Rows are not inserted or deleted. Receipt keys are not rewritten. A formula is not replaced.

A local `.xlsx` uses the same cells. The bot's `migrate_v21_settings` helper refuses to save if a number or a formula in the grid changed.

Made by SkybatanX (@SkyXFunNext).
