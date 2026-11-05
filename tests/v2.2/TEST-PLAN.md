# Family Book v2.2 test plan

This plan is for a person testing by hand. Do not merge the pull request until these cases pass and you say so. Do not use a tester bot. Do not use a real household book, a real card, or a real address. Use a Google account or a computer folder you control, the made-up names below, and the amount 12.34.

Made-up names used here:

- Owner inbox: `gmail/family@example.com`
- Member inbox: `outlook/alex@example.com`
- Display names: Mom, Alex
- Store: Costco
- Amount: 12.34

`python3 tests/v2.2/check_v22.py` is the offline check. It does not start Excel and it does not talk to a bot. It should print `v2.2 offline checks passed`. Run it before the hand cases. The hand cases are still required. Cases 9 and 10 also lean on that script, because a person cannot inject a bad write into the bot.

Receipt file names stay `YYYY-MM-DD HHMM - Store - TOTAL.ext`. A tester file may be prefixed `TEST - ` only when the case says that copy must be ignored.

## What a real book is

Open Annual Summary.

- `B46` is `Book version` and `F5` is a four-digit year, or
- the book is old enough that `B46` was never added: `B2` starts with `Family Book`, `F5` is a year, and a Jan sheet exists.

A spreadsheet with none of that is not a book. Trash, a name that starts with `TEST -` or `Copy of`, and anything inside `Family Book - Backups` or `backups` is not a candidate.

## 1. Fresh install, no books

Use an account that has no `Family Book` folder and no `Family Book - YYYY` workbook. Install the bot from this branch's files (or from the pull request after you point a test bot at those files yourself). Say hi.

**Expect**

- One question: where to save receipts and the report. With a desktop computer connected, the choices are Google Drive and Google Sheets, OneDrive and Excel Online, or an Excel file on this computer. With no computer, the local choice is absent.
- No question about a bank, a card, or a statement.
- After you pick a place, one book is created. Annual Summary `C46` is `v2.2`, `C47` is `off`, `C48` is `not yet`, and `F5` is the current year.
- A Bot State sheet exists. Row 1 starts with `Managed by Family Book bot, please don't edit.` `B4` is `v2.2`. On an `.xlsx` the sheet is hidden. On Google Sheets it may be visible. That is correct. The bot does not ask you to hide it.
- Transactions and Cards have no data rows.
- The bot invites a receipt.

Send one cash receipt for Costco, 12.34, dated today. The file name is `YYYY-MM-DD HHMM - Costco - 12.34.ext` with today's date. The grid gains 12.34 once.

## 2. Reinstall with one 2026 book

Start from the book in case 1, or any one real `Family Book - 2026` you own. Put these facts on it before you delete the bot:

- Bot State row 31: Inbox `gmail/family@example.com`, Last scan `2026-11-03T20:00:00Z` (use a stamp two days before the day you test, if that day is not 5 November 2026).
- Log row 2, column A: `email gmail/family@example.com 18c3fab`
- Log row 2, column B: a date inside the last month, for example `2026-10-20`
- Oct `O6` = 12.34 if that cell is empty. Write down the cell you use.
- One daily receipt scan routine, one spending report, and one new-year routine. Card-due and statement-ready stay absent while `C47` is `off`.

Delete the bot, or clear its memory, and install it again. Do not delete the spreadsheet. Say hi. Do not paste a link.

**Expect**

- The bot says it reconnected to Family Book - 2026. It does not ask where to save the book. It does not create a second book.
- It does not say it is scanning the whole mailbox or the last 30 days.
- The search window it names starts at the saved scan time minus 2 days. On the example stamp, that is 1 November 2026 at 20:00 UTC, not 1 January and not "all mail".
- Message `18c3fab` is not logged again. Oct `O6` is still 12.34.
- Open the routine list. There is still one daily receipt scan, one spending report, and one new-year routine. Say hi again. The counts stay at one.
- Bot State still has the owner inbox. After a scan finishes, that inbox's last-scan time moves forward. A failed scan leaves the old time.

## 3. Reinstall with only last year's book

Remove the 2026 book from the test account, or use a different account. Leave one real book: `Family Book / Family Book - 2025 / Family Book - 2025`. `F5` is 2025. `B46` is `Book version`. Put 40.00 in a 2025 month cell and write down the cell.

Clear the bot's memory and say hi.

**Expect**

- It reconnects to the 2025 book and says so. It does not create an empty second household.
- It may create `Family Book - 2026` inside the same `Family Book` folder, and it says that this year's book was missing. The 2025 amount you wrote down is unchanged.
- It does not ask the storage question.

## 4. Look-alikes, copies, and trash

On one Drive, keep the single real `Family Book - 2026` from case 2. Also add all of these, and do not delete the real book:

- A folder or file named `TEST - Family Book - 2026`
- A file named `Copy of Family Book - 2026`
- The real book moved to trash, then restored, plus a second copy left in trash
- A spreadsheet named `Family Book - 2026` whose Annual Summary `B46` is `Notes` and whose banner does not start with `Family Book`

Clear memory and say hi.

**Expect**

- The bot reconnects to the one real book. It does not ask which file.
- It does not mention the `TEST -` copy, the `Copy of` file, the trashed copy, or the Notes spreadsheet as candidates.
- The real book's 12.34 is unchanged.

Then make a second real root: another folder named `Family Book` that also contains a real year book (`B46` and `F5` filled). Clear memory and say hi.

**Expect**

- The bot asks which set. It lists both places and their years. It does not pick one and it does not create a third book.

## 5. Shared book, member join

Share only the year folder `Family Book - 2026` with a second account, as an editor. Do not share the `Family Book` root. On the second account, install the bot with empty memory. That account owns no Family Book of its own. Say hi. Do not paste a link unless the bot cannot see the share.

**Expect**

- It joins as a member and names the shared book.
- It does not create a `Family Book` root and it does not move the owner's folders.
- It asks for a display name only if Bot State does not already list one. You can skip.
- It does not run the migration. If `C46` is older than `v2.2`, it says the owner's bot will update the book.
- It does not create the new-year routine. It may create the daily scan, if an inbox is connected, and the spending report. One of each.

## 6. v1.2.3 book, backup, and amount check

Make a copy of a real book into the test account and name the copy's year folder so it is the only book the bot will see (move other test books aside). Edit this copy by hand before you talk to the bot:

1. Set Annual Summary `C46` to `v1.2.3`.
2. Clear `C47` and `B47` on Annual Summary.
3. Delete the Bot State sheet if it is there.
4. On every month sheet, set `B47` to `Receipts this month` and `B48` to `Date & time`. Remove a Transactions title if one remains.
5. Clear Log `N1` and `O1` if you want this to look like v1.2.3 rather than v1.2.4. Either way the chain continues to v2.2.
6. Put 12.34 in Jan `K6` and 80 in Jan `C19`. Write both down. Do not use a formula.

Say hi, as the owner.

**Expect**

- One line that it is updating the book to v2.2 and that amounts stay as they are.
- Before `C46` changes, `Family Book - Backups` contains a copy. The name looks like `Family Book - YYYY - before-v1.2.3 - YYYYMMDD-HHMMSS` or the next step name if the v1.2.3 step was already considered done. There is a backup for each step that runs.
- When it finishes, `C46` is `v2.2`, Bot State `B4` is `v2.2`, and a Transactions section exists.
- Jan `K6` is still 12.34 and Jan `C19` is still 80. No other typed number in rows 1–44 changed.
- The bot does not ask you to retype the numbers.

## 7. Blank C46

Take a current v2.2 book. Confirm it has `Transactions this month` and `C47` is `off` or `on`. Clear `C46` only. Leave 12.34 where it is. Delete Bot State. Clear memory and say hi, as the owner.

**Expect**

- It does not rebuild the book from v1.0 and it does not insert the receipt list again.
- It adds Bot State and sets `C46` back to `v2.2`.
- 12.34 is unchanged.
- A backup exists from the v2.2 step.

## 8. Book newer than the bot

On a copy, set `C46` to `v2.3`. Leave 12.34 in place. Say hi.

**Expect**

- The bot says the book is Family Book v2.3, which is newer than this bot (v2.2), and that it will not change the book.
- `C46` is still `v2.3`. 12.34 is unchanged. No backup was taken in order to edit. No new receipt is written.

Set `C46` back to `v2.2` when you are done, or throw the copy away.

## 9. A failed step restores the backup

Two checks.

**Offline, required.** From the repo:

```text
python3 tests/v2.2/check_v22.py
```

**Expect** the last line is `v2.2 offline checks passed`. That run writes 99 into a copy, sees the amount change, and puts 12.34 back. The live file does not keep 99.

**By hand.** On a local copy, note Oct `O6` (or the cell you used) and the file's modified time. Ask the owner bot to update a v2.1 copy (case 7 is enough). When it finishes:

- `Family Book - Backups` has the pre-step file.
- Open that backup. The noted amount matches the live book.
- If the bot ever says a step failed and it restored a backup, the live amount matches the backup and the bot does not continue to the next step in that conversation. Do not tell it to retry immediately.

## 10. Running the migration again is a no-op

On the book that case 6 or case 7 already brought to v2.2, ask the bot to update the book again. Or clear memory, reconnect, and let the next run check the version.

**Expect**

- It does not say it is updating.
- `C46` stays `v2.2`. Bot State stays. 12.34 stays.
- `Family Book - Backups` does not gain another file from this second run.
- The offline script checks the same no-op. You do not need a second pass of the script if case 9 already passed.

## 11. Resume from the Log when Bot State has no scan time

Use the reconnected 2026 book. Delete the inbox rows on Bot State (rows 31–50). Leave one Log row: column B `2026-10-20`, column C `Costco`, column D `12.34`. Leave `C52` as a date in January, for example `2026-01-15`. Trigger the daily scan, or ask it to scan mail.

**Expect**

- The window starts at 13 October 2026 (20 October minus 7 days), not at 15 January and not at the beginning of the mailbox.
- It says that date, or a search `after:` that date.
- The 12.34 already on the Log is not added again.

Then clear the Log dates as well, leave `C52` as `2026-01-15`, and scan again with a fresh inbox row.

**Expect** the window starts at 15 January 2026 (`C52`), still not at the first message in the account.

Then clear `C52` too, on a book that has never had a Log row. 

**Expect** the last 30 days only, plus one line that older receipts from this year can be backfilled if you ask. That 30-day path is only this empty book.

## 12. A member writes only its own scan time

On the shared book, Bot State has two inbox rows:

| Inbox | Last scan |
|---|---|
| `gmail/family@example.com` | `2026-11-01T20:00:00Z` |
| `outlook/alex@example.com` | empty, or an older stamp |

`B5` (Storage) is `google`. Row 18 is Alex, member.

As the member bot, with only `outlook/alex@example.com` connected, run a scan.

**Expect**

- The Alex inbox's last-scan time updates.
- `gmail/family@example.com` is still `2026-11-01T20:00:00Z`.
- Storage is still `google`. The Alex member row is unchanged except that you did not need to edit it.
- The member bot does not change `C46`.

As the owner bot, scan only the Gmail inbox.

**Expect** the Gmail stamp moves and the Alex stamp stays at whatever the member wrote.

## Done

You are done when:

- `python3 tests/v2.2/check_v22.py` prints `v2.2 offline checks passed`
- Cases 1 through 8 and 10 through 12 match the expects above
- Case 9's script passed, and a hand migration left the noted amount in place with a backup beside it

Main stays on v2.1 until you merge. The template download link in the skills still points at `main` on purpose. After you merge, that link serves v2.2.

Made by SkybatanX (@SkyXFunNext).
