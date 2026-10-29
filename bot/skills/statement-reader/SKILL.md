---
name: statement-reader
description: "Read a card or bank statement into normalized lines and metadata, and refuse to write when the per-card totals do not match. Use for a PDF, CSV, photo, or pasted HTML or text statement."
---

# Statement reader

Turn a credit-card or bank statement into statement metadata plus normalized lines. This skill does not categorize and it does not write the grid. The transaction-category skill categorizes. The receipt-match skill links and dedupes. The family-book skill writes, and only after the totals check below passes.

The connector cannot hide tabs, cannot read cell formats, and takes sizes in pixels. This skill does not restyle the sheet. It does not store a full card number or a full account number. Keep the last 4 only.

## Save the original first

Before any parse, save the file the user sent, untouched, in the book for the statement date's year:

`Family Book - {year}/statements/{Issuer Product}-{last4}/YYYY-MM-DD statement.ext`

`{year}` and `YYYY-MM-DD` are the statement date. `{Issuer Product}` is the short product name from the table below, and `{last4}` is the primary card on the account (the first card the statement names). Example: `Family Book - 2026/statements/CIBC Visa-1001/2026-09-27 statement.pdf`. One statement is one file. An extra card on the same account links to that same file. Do not save a second copy of the same bytes.

Two statements for the same card and the same statement date are one statement. The same key or the same SHA-256 is a no-op. Different content asks which file to keep. Do not overwrite the first file and do not save the second as `statement - 2`. A receipt file that is a different purchase still uses ` - 2` before the extension. A re-sent file whose SHA-256 is already in the Log is not a collision.

If the totals check below refuses the import, keep the saved copy. Rename it, or save it, with ` - not imported` before the extension: `2026-09-27 statement - not imported.pdf`. Append a Log row whose Source is the reason (`card 1001 lines sum to 71.04, statement says 99.99`). Do not write a grid amount and do not add a Statements bill. The file is still there.

## What to keep

- Issuer and product.
- Every card on the account: last 4, and the holder only when a name is printed on the same line as that card's number. `Prepared for` and `Account holder` are the account line. They do not fill Holder. If no name is printed beside the number, leave Holder blank. Do not invent a name. The synthetic fixtures print Jordan Lee only as `Prepared for`, so those cards have a blank holder. Account cards on the Cards sheet lists every last 4, for example `1001, 1002`.
- Statement date, period start, period end, payment due date, minimum payment, amount due.
- The issuer spend category when the line prints one (CIBC does).
- For each purchase or return: transaction date, post date, description, signed amount, last 4, FX note.

Card label, written in the Transactions Card column and on the Cards tab: `{issuer} {product}-{last4}`. Statement id: `{Issuer Product}-{last4 of the account's first card}-{statement date}`, for example `CIBC Visa-1001-2026-09-27`. Bank label: `{bank} {Chequing/Savings}-{last4}`.

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
- The description you store and show is the printed text: strip a leading marker, join a wrapped line, collapse whitespace. Keep `&`. `T&T` stays `T&T`. Do not rewrite it as `AND`. The key uppercases that text and still keeps `&`.
- Matching uses a separate folding: lowercase, and `&` becomes `and`. That folding is not what you write in the Description cell or in the key.
- A merchant map entry reconciles a store with and without a city. `Costco Burlington` and `Costco` are the same merchant when the map, or the brand, is Costco. Learn the brand, not the city.
- Occurrence numbers lines that share last 4, post date, amount, and the stored description, in the order they appear, starting at 1. A unique line is still `|1`.
- The file and the Statements row use the statement date's year. Each line is written in the book for its **post date's** year. When the purchase date and the post date are in the same year, the month sheet and the day column are the purchase date. When they are not, use the post date's month and day in that post-date year's book, and keep the purchase date in Trans date. A Dec 31 purchase that posts Jan 2 is written in the January book's January sheet. If that year's book does not exist, ask once to create it, and do not write the line until it does. Do not ask a second time.

## Markers, wraps, FX, cards, payments, returns

**Markers.** CIBC prints `Ý` (U+00DD) in front of some merchants. Strip that character, and a lone leading `Y` that is only the cash-back flag. It is not part of the description or the key.

**Wrapped description.** A merchant line can break before the city, and the amount can sit on the following line. Join continuation lines onto the description until the amount. A line that is only an issuer spend category is the category, not more description. Known issuer categories: Transportation; Restaurants; Retail and Grocery; Personal and Household Expenses; Hotel, Entertainment and Recreation; Health and Education; Professional and Financial Services; Home and Office Improvement; Other Transactions.

**Foreign currency.** A line such as `FOREIGN CURRENCY USD 6.40 @ 1.425` is a note on the purchase. It is not its own row. The amount you keep is the CAD (book currency) amount billed. Store the note as `FOREIGN CURRENCY USD 6.40 @ 1.425`.

**Several cards.** A `Card number` or `Purchases - Card #` header switches the last 4 for the lines under it. One account can list a primary card and an authorized user. Each line keeps the last 4 of the header above it.

**Payments.** These are not expenses: `PAYMENT THANK YOU`, `PAIEMENT MERCI`, `BANK PAYMENT`, `PAIEMENT BANQUE`. Each one is a Transactions row, category `Card payment`, with a generated key. It is not a grid amount. It applies to the latest statement for that card dated on or before the payment's post date. Paying that bill in full also marks every older unpaid bill for the card paid, because the balance carries forward. A partial payment reduces only the latest bill. An overpayment is a credit on Cards. Nothing goes negative. A payment with no eligible bill changes nothing. Recording this statement does not by itself mark its amount due paid.

**Returns.** A negative amount is a return. Keep it. The receipt-match skill links it to the original purchase when the card, the merchant, and the absolute amount match and the purchase posted first.

**Detail blocks that repeat a purchase.** Triangle's "Details of your Sport Chek store purchases" says the total is already in the Purchases section. Do not create lines from that block.

**Privacy.** If the text contains a 13 to 19 digit number, keep only the last 4. Do not write the rest anywhere, including the Log, the file name, or chat.

## Totals check, before any write

Sum the non-payment lines for each card, returns included as negative. Compare that sum to the statement's own per-card total (`Total for … 1001`). They must match to the cent.

- If they do not match, write nothing. Tell the user the card, the sum you got, and the total printed on the statement.
- A partial or mid-month CSV never creates a bill. Only a statement with an amount due does. Write the CSV's purchase lines. Do not add a Statements row and do not set Last amount due from that file. That file may still add a Cards row with issuer, product, and last 4 only. Leave Last amount due, Paid status, and the statement file blank. The later full statement uses the same transaction keys and adds only the new lines, and that full statement is the bill.
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

A period that crosses a month is normal. A period that also crosses a year (December 20 to January 19) still keys each line by post date. The file and the Statements row stay in the statement-date year. Each line is written in the post-date year's book.
