---
name: statement-reader
description: "Read a card or bank statement into normalized lines and metadata, and refuse to write when the per-card totals do not match. Use for a PDF, CSV, photo, or pasted HTML or text statement."
---

# Statement reader

Turn a credit-card or bank statement into statement metadata plus normalized lines. This skill does not categorize and it does not write the grid. The transaction-category skill categorizes. The receipt-match skill links and dedupes. The family-book skill writes, and only after the totals check below passes.

The connector cannot hide tabs, cannot read cell formats, and takes sizes in pixels. This skill does not restyle the sheet. It does not store a full card number or a full account number. Keep the last 4 only.

## Save the original first

Before any parse, save the file the user sent, untouched, in that statement's year folder:

`Family Book - {year}/statements/{Issuer Product}-{last4}/YYYY-MM-DD statement.ext`

`{year}` and `YYYY-MM-DD` are the statement date. `{Issuer Product}` is the short product name from the table below, and `{last4}` is the primary card on the account (the first card the statement names). Example: `Family Book - 2026/statements/CIBC Visa-1001/2026-09-27 statement.pdf`. One statement is one file. An extra card on the same account links to that same file. Do not save a second copy.

## What to keep

- Issuer and product.
- Every card on the account: last 4, and the holder when the statement prints one. An extra card with no printed name has a blank holder. Do not invent a name.
- Statement date, period start, period end, payment due date, minimum payment, amount due.
- The issuer spend category when the line prints one (CIBC does).
- For each purchase or return: transaction date, post date, description, signed amount, last 4, FX note.

Card label, written in the Transactions Card column and on the Cards tab: `{issuer} {product}-{last4}`. Bank label: `{bank} {Chequing/Savings}-{last4}`.

| Statement words | Issuer | Product | Label example |
|---|---|---|---|
| CIBC Dividend Visa | CIBC | Visa | `CIBC Visa-1001` |
| CIBC Costco Mastercard | CIBC | Costco MC | `CIBC Costco MC-2202` |
| Triangle World Elite Mastercard | Triangle | MC | `Triangle MC-3303` |
| Rogers Bank Mastercard | Rogers | MC | `Rogers MC-4404` |

## Statements have no transaction id

The key is `last4|YYYY-MM-DD|amount|NORMALIZED DESCRIPTION|occurrence`.

- The date is the **post date**. Statement periods are by post date, so each line belongs to one statement. A purchase on Aug 21 that posts on Aug 24 belongs to the statement whose period contains Aug 24.
- Amount is two decimals, with a leading minus for a return (`-57.53`). No commas.
- Normalize the description: strip a leading marker, turn `&` into `AND`, uppercase, collapse whitespace.
- Occurrence numbers lines that share last 4, post date, amount, and normalized description, in the order they appear, starting at 1. A unique line is still `|1`.
- The month sheet is the month of the **transaction date** (the day it happened). A Dec 31 transaction that posts Jan 2 is written on the December sheet of that December's year book. The file still lives under the statement date's year.

## Markers, wraps, FX, cards, payments, returns

**Markers.** CIBC prints `Ý` (U+00DD) in front of some merchants. Strip that character, and a lone leading `Y` that is only the cash-back flag. It is not part of the description or the key.

**Wrapped description.** A merchant line can break before the city, and the amount can sit on the following line. Join continuation lines onto the description until the amount. A line that is only an issuer spend category is the category, not more description. Known issuer categories: Transportation; Restaurants; Retail and Grocery; Personal and Household Expenses; Hotel, Entertainment and Recreation; Health and Education; Professional and Financial Services; Home and Office Improvement; Other Transactions.

**Foreign currency.** A line such as `FOREIGN CURRENCY USD 6.40 @ 1.425` is a note on the purchase. It is not its own row. The amount you keep is the CAD (book currency) amount billed. Store the note as `FOREIGN CURRENCY USD 6.40 @ 1.425`.

**Several cards.** A `Card number` or `Purchases - Card #` header switches the last 4 for the lines under it. One account can list a primary card and an authorized user. Each line keeps the last 4 of the header above it.

**Payments.** These are not expenses and they do not get a key: `PAYMENT THANK YOU`, `PAIEMENT MERCI`, `BANK PAYMENT`, `PAIEMENT BANQUE`. A payment on this statement paid the previous bill. This statement's amount due stays unpaid until a later bank payment, the next statement, or the user says it is paid.

**Returns.** A negative amount is a return. Keep it. The receipt-match skill links it to the original purchase when the card, the merchant, and the absolute amount match and the purchase posted first.

**Detail blocks that repeat a purchase.** Triangle's "Details of your Sport Chek store purchases" says the total is already in the Purchases section. Do not create lines from that block.

**Privacy.** If the text contains a 13 to 19 digit number, keep only the last 4. Do not write the rest anywhere, including the Log, the file name, or chat.

## Totals check, before any write

Sum the non-payment lines for each card, returns included as negative. Compare that sum to the statement's own per-card total (`Total for … 1001`). They must match to the cent.

- If they do not match, write nothing. Tell the user the card, the sum you got, and the total printed on the statement.
- A mid-month CSV that says it is a partial export has no full-statement total. Check that its own rows add up to the total it prints, when it prints one, then write those rows. The later full statement uses the same keys and adds only the new lines.
- Photos are read the same way as text once the merchant lines, dates, and amounts are visible. If a page is unreadable, say so and do not guess a line.

## CSV and HTML

A CSV header is `trans_date,post_date,description,amount,last4`, with optional `spend_category` and `fx`. Comment lines (`# issuer:`, `# product:`, `# statement_date:`, `# period_start:`, `# period_end:`, `# due_date:`, `# minimum:`, `# amount_due:`, `# partial:`) hold the metadata. Dates are `YYYY-MM-DD`.

Pasted HTML is the same statement with the tags removed. Read the text, not the markup. A `<pre>` block or a table of one transaction per row both work.

## Layouts the reader must accept

The synthetic fixtures in `tests/v2.0/fixtures/` are the shapes. Real statements are not stored in this repo.

- **A, CIBC Visa.** `Ý` marker, spend category on the next line, two card numbers, a wrapped merchant, identical twin lines, `PAYMENT THANK YOU/PAIEMENT MERCI`.
- **B, CIBC Costco Mastercard.** Same CIBC shape, one card, a purchase whose transaction date is just before the period and whose post date is inside it.
- **C, Triangle Mastercard.** Payments, returns, and purchases in separate blocks. A Sport Chek detail block that must not become extra lines. A `BANK PAYMENT/PAIEMENT BANQUE` line.
- **D, Rogers Mastercard.** Narrow columns, often one word per line. A wrapped merchant, a `FOREIGN CURRENCY` note, and a payment.

A period that crosses a month is normal. A period that also crosses a year (December 20 to January 19) still keys each line by post date and places the grid row in the transaction date's month and year book.
