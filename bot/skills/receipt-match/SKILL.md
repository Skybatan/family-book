---
name: receipt-match
description: "Link a receipt to a statement line, keep the v1.2.4 dedupe rules, and never add the same amount twice. Question rows hold no grid amount."
---

# Receipt to transaction matching

Use this after the statement reader and the category skills, and before the family-book skill writes an amount. The v1.2.4 rules in the family-book skill still apply. This skill adds the statement link. Gather every candidate before you write. Do not stop at the first hit.

## Keys

A statement line's key is `last4|post date|amount|normalized description|occurrence`. The same key is the same line. Re-reading a statement, or importing a mid-month CSV and then the full statement, adds nothing for a key that is already on the Log.

A receipt is the same purchase as another receipt by the v1.2.4 rules:

1. Same receipt number at the same merchant, even when the dates are far apart.
2. No number on at least one side: same merchant (full match), same total to the cent, dates within ±1 day.
3. Near match: ask. Same merchant and same total more than 1 day apart and at most 7 days apart. Or the same merchant and a small total gap (the greater of 5.00 and 15% of the larger amount) on the same day or within ±1 day, the same window as rule 2. Costco 42.00 on Oct 7 is a near match of Costco 41.00 on Oct 6. Or a partial merchant name. Do not guess.

A fuel AUTH code is not a receipt number. `48291` and `#48291` are the same number. Different numbers are different purchases.

## Auto-link a receipt to a statement line

All of these:

- The amounts match to the cent.
- The receipt date is 0 to 3 days before the post date.
- The store is a full merchant match for the description (`Costco` matches `COSTCO WHOLESALE W253 BURLINGTON ON`, `Shell` matches `SHELL C11318 MISSISSAUGA ON`).
- If the receipt shows a last 4, it matches the line. A receipt with no last 4 can still match.

Then set the transaction Status to `matched`, put the receipt number in Receipt #, and put the transaction key on the receipt. Do not write the amount again.

## Ask, and write no grid amount

- The totals differ by a tip or by FX, the store is a full or partial match, and the dates are inside the 3-day window.
- The store is unclear.
- More than one line fits.
- A v1.2.4 rule 3 near match, and no rule 1 or rule 2 hit.

One question. Status `question`. Where written stays blank. A later copy of the same question joins that row. On a yes, link and do not add. On a no, the question row becomes its own purchase and then follows the write order.

## Which source fills the grid

- **Receipt first** (a card receipt, no statement line yet). Fill the grid from the receipt's item split. Receipts Status `pending`. Log Status `awaiting statement` once the write finishes. The line is waiting for its statement, and the amount is already in the grid.
- **Statement first.** Fill the grid with the transaction category for the whole amount. Transactions Status `no receipt`.
- **Statement arrives after the receipt.** Link. Leave the grid as the receipt split. Do not add.
- **Receipt arrives after the statement.** Link. Replace the single category amount with the item split so the parts still add up to the same total. Record the new cells on the Log before changing numbers. Clear the old cell if the split uses different cells. A retry sees the recorded cells and does not add.
- **Cash.** Payment is cash. Fill the grid from the items. Receipts Status `cash`. It never waits for a statement.
- **Return.** Negative row. Link it to the earlier purchase on the same card with the same merchant and the opposite amount. The grid gets the negative amount in that category. A return is not a duplicate of the sale.

## Dedupe rules that stay in force

- Gather every candidate first. Auto-attach only when there is exactly one candidate. Two or more candidates are one question that lists every one of them. Do not add an amount while that question is open.
- A `question` row holds no grid amount.
- A confirmed duplicate is Status `superseded`. Do not delete the row.
- Photo and email of the same receipt are one receipt row. The second file is attached (`photo` then `email` in the sources). The File cell (Receipts column AA) is `photo +1` when there is a second file. A pasted text receipt uses the File label `text`.
- A receipt with no card is status `cash`.
- Different receipt numbers are different purchases. Do not ask, and do not flag them as one purchase.
- Every write is idempotent. Append the pending Log row with the target cell already in Where written, then write that cell, then save the file (the same step as family-book section 3 step 9), then the section row, then the finished status. A retry that finds the pending row reads the recorded cell. A pending row with the same receipt key is that resume, not a rule 2 match. If Where written is blank, search that day's category block, including each item cell of a split and Fixed Expenses or Income rows, for this amount and item text that contains the short store name. Record that cell and write nothing. Only if none is found, use the first empty cell. On a match, files keep their own names.

## Write order

This is the same order as family-book section 3. Step 9 is the file, after the amount.

1. A statement's original bytes are already in the statements folder. The statement-reader skill saved them before parsing. A refused import keeps that copy under a ` - not imported` name. Do not save it again here, and do not write a grid amount for it.
2. Read the Log and both sections. Skip `superseded`.
3. On a match or a known key: attach or link, stop, do not touch amounts.
4. On a question: one Log row, no grid amount, stop.
5. New purchase: append a `pending` Log row that already names the cell in Where written. Then write the grid. Then save the receipt file, or record the statement path (family-book section 3 step 9). Then the Transactions or Receipts row. Then set the finished status.

A return lookup checks refunds before it quotes a window. If a negative line or credit already matches the receipt, say it was already refunded on that line's post date.

The Transactions and Receipts sections are not part of any total. The grid is the only place an amount counts.
