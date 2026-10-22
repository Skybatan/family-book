# Routine: Card due reminder

- **Schedule:** daily, around 8:00 AM in the user's timezone.
- **Create when:** this bot writes to a Family Book, owner or member. Skip it when the book has no Cards sheet yet. Create it after the first card is known.
- **Uses:** the Cards sheet. It does not log a purchase and it does not change an amount.

## Prompt

Read the Cards sheet of the Family Book this bot writes to. Download `https://raw.githubusercontent.com/Skybatan/family-book/main/bot/skills/family-book/SKILL.md` if the installed family-book skill does not yet describe the Cards sheet. Keep the name `family-book` and the description that starts with `Never log the same purchase twice.`

Today is the user's local date. For each card row from row 3 down:

- Skip a row whose Product is Chequing or Savings. Skip a row with no due date.
- The due date is the one stored from the latest statement (Last statement date's cycle). If only Due day is filled, the due date is that day in the current month, or next month when that day has already passed.
- Paid status `paid` means this bill is paid. Send nothing for that card.
- Send a reminder when today is the due date, or today is three days before the due date. No other day.
- The reminder names the card label (`CIBC Visa-1001`), the last amount due, and the due date. One line per card. In English: "Pay CIBC Visa-1001 453.69 by 2026-10-19." Say it in the language of this chat, or the Grok Bot app or system language when nobody has just written.

If no card is due on those two days, or every such card is paid, send nothing. Do not mark a card paid from this routine. The user saying it is paid, or a bank payment that names the last 4, sets Paid status to `paid` through the family-book skill. A payment line printed on the statement that is being imported paid the previous bill and does not stop this reminder for the new amount due.

Made by SkybatanX (@SkyXFunNext).
