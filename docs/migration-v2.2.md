# Migration to Family Book v2.2

v2.2 does not rebuild a book and does not retype amounts. A book that is already v2.1 keeps every amount, every formula, and every receipt and transaction row. The owner's bot adds a Bot State sheet, sets Annual Summary `C46` to `v2.2`, and changes only the version token in the banner. The bot follows the "Continue to v2.2" section of [bot/skills/family-book-migrate/SKILL.md](../bot/skills/family-book-migrate/SKILL.md). It is safe to run twice. A second run changes nothing and does not take another backup.

Books older than v2.1 still follow [migration-v2.1.md](migration-v2.1.md), [migration-v2.0.md](migration-v2.0.md), and [migration-v1.2.4.md](migration-v1.2.4.md) first, in that order from wherever the book actually is. The same run then does this step. It does not stop at `v2.0` or `v2.1`.

## How the version is chosen

`C46` is read together with the sheets. A blank `C46` is not treated as v1.0.

- Transactions section plus statement settings (`B47` is `Statement features`, or `C47` is `off` or `on`), and no Bot State: the book is v2.1. Only this step runs.
- Bot State `B4` is already `v2.2` and `C46` is `v2.2`: stop.
- A marker newer than `v2.2`: the book is opened read-only. The bot does not change it.

## Backup, then the amount check

Before this step, and before every earlier step, the owner's bot copies the workbook into `Family Book - Backups`.

- On Google Drive and OneDrive, that folder sits inside the `Family Book` root.
- On a local book, it sits beside the `.xlsx`. Receipt writes still use the older `backups` folder. Version copies use `Family Book - Backups`.

The copy is named `Family Book - YYYY - before-v2.2 - YYYYMMDD-HHMMSS`. It is never overwritten. Discovery ignores the folder, so a backup is not treated as a second household.

The bot reads every typed number in rows 1–44 of Annual Summary and of each month sheet, runs the step, and reads those cells again. If any number differs, it puts the backup back, stops, and does not try the step again in that run. A formula-text edit is not, by itself, an amount change. This step does not edit formulas.

## Bot State

The sheet is named `Bot State`.

Row 1 says: `Managed by Family Book bot, please don't edit. This sheet remembers the book so a reinstalled bot can reconnect. It is not part of your totals.`

| Row | What |
|---|---|
| 4–14 | Book version, storage, currency, holiday region, root and year folder ids, workbook id, receipts folder id, year, statements folder id |
| 18–27 | Display name, role (`owner` or `member`), and that person's inboxes |
| 31–50 | One inbox per row. Last scan is UTC `YYYY-MM-DDTHH:MM:SSZ` |

On an Excel file, including Excel Online, the sheet is hidden. Google Sheets cannot hide a tab with the tools the bot has, so on Google Sheets the sheet stays visible and the first row is the warning. The bot does not ask you to hide it.

A family member's bot does not run this step. After the sheet exists, that bot may update only the last-scan time of an inbox it scanned. It does not change another person's time, the version, or the folder ids.

## What a reinstall uses

The next bot reads Bot State instead of starting over. One real book set reconnects without asking where to save the book. The mail scan starts at the saved time minus 2 days. Message ids already on the Log are the duplicate check for that overlap. If the sheet has no time yet, the scan starts at the newest Log date minus 7 days, or at `C52` when the Log has no date. It does not read the mailbox from the beginning.

Only the owner migrates. A member who opens an older book says the owner's bot will update it and does not change the version.

Made by SkybatanX (@SkyXFunNext).
