# Routine: Statement ready

- **Schedule:** daily, with the receipt scan (around 8:00 PM in the user's timezone). It can also run on its own at 9:00 AM if the scan is not created yet.
- **Create when:** the owner started the book. A member does not send this nudge.
- **Uses:** the daily mail scan and the Cards sheet. It does not log a purchase.

## Prompt

Look for a statement-ready email, and look at the Cards sheet.

1. During the daily scan, an email whose subject or first lines say the statement is ready (for example "Your CIBC Visa statement is ready") is this nudge, not a receipt. Match the issuer or the product to a Cards row. Reply once: "Statement ready for CIBC Visa-1001: forward or download it." Use the real label. Say it in the language of this chat. Do not log the email as a purchase. Do not download a statement that the email does not attach. If the email has the PDF attached, save it with the statement-reader skill and import it. That import ends the nudge for this cycle.
2. When there is no such email, nudge a few days after the usual statement day. A card's Statement day is on the Cards sheet. Three days after that day in the current month, if this month's statement is not already imported, send: "Statement should be out for CIBC Visa-1001." Skip Chequing and Savings rows. Skip a card whose last statement date falls in the current month. One line per card. Do not send it on the statement day itself, or on the next day, or on the day after that.
3. Stop for a card once a statement whose statement date is in the current month is on the Statements sheet or named in that card's Statement file. A later month starts the nudge again.
4. If nothing is ready and no card is past the three-day mark, send nothing.

The statements folder is `Family Book - {year}/statements/{Issuer Product}-{last4}/`. The file name is `YYYY-MM-DD statement.ext`, and the date is the statement date.

Made by SkybatanX (@SkyXFunNext).
