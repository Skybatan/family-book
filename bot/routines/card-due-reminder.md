# Routine: Card due reminder

- **Schedule:** daily, around 8:00 AM in the user's timezone.
- **Create when:** this bot writes to a Family Book, owner or member. Skip it when the book has no Cards sheet yet. Create it after the first card is known.
- **Uses:** the hidden Statements sheet. Cards shows only the latest statement and is not the source of the due date. This routine does not log a purchase and it does not change an amount.

## Prompt

Read the Statements sheet of the Family Book this bot writes to. Download `https://raw.githubusercontent.com/Skybatan/family-book/main/bot/skills/family-book/SKILL.md` if the installed family-book skill does not yet describe statement bills. Keep the name `family-book` and the description that starts with `Never log the same purchase twice.`

Today is the user's local date. For each Statements row:

- Skip a row whose Paid status is `paid`. Skip a row with no due date. Skip a bank account (Chequing or Savings). Skip a row whose due date has already passed.
- The due date is the full date in the Due date column. Do not build a date from the Due day on Cards.
- Send a reminder when today is that due date, or today is three days before it. No other day. One line per unpaid statement. An older unpaid statement is included even when Cards already shows a newer statement.
- The amount is Amount remaining when that cell has a number, otherwise Amount due. Write it with two decimals. End the sentence with a period. In English: "Pay CIBC Visa-1001 495.79 by 2026-10-19."
- If both amount cells are blank, the amount words are exactly `check your statement for the amount`. In English: "Pay CIBC Visa-1002 check your statement for the amount by 2026-10-19." Never leave the amount blank, and never send "Pay CIBC Visa-1002  by 2026-10-19."
- Say it in the language of this chat, or the Grok Bot app or system language when nobody has just written. Keep the amount and the date. Keep the period.

If no unpaid statement is due on those two days, send nothing. Do not mark a bill paid from this routine. A card payment applies to the latest statement for that card dated on or before the payment's post date. Paying that bill in full also marks every older unpaid bill for the card paid. A partial payment reduces only the latest bill, and this reminder continues for each unpaid bill whose due date has not passed. An overpayment is a credit on Cards. Nothing goes negative.

Made by SkybatanX (@SkyXFunNext).
