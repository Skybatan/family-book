# Routine: Statement ready

- **Schedule:** daily, with the receipt scan (around 8:00 PM in the user's timezone). It can also run on its own at 9:00 AM if the scan is not created yet.
- **Create when:** the owner started the book. A member does not send this nudge.
- **Uses:** the daily mail scan and the Cards sheet. It does not log a purchase.

## Prompt

Look for a statement-ready email, and look at the Cards sheet.

1. During the daily scan, an email whose subject or first lines say the statement is ready (for example "Your CIBC Visa statement is ready") is this nudge, not a receipt. Match the issuer or the product to a Cards row. Reply once: "Statement ready for CIBC Visa-1001: forward or download it." Use the real label. Say it in the language of this chat. Do not log the email as a purchase. Do not download a statement that the email does not attach. If the email has the PDF attached, save it with the statement-reader skill and import it. That import ends the nudge for this cycle.
2. Each card gets at most two nudges per cycle, then this routine stops until the next cycle.
   - The first nudge is on the day the statement is expected. That day is the Statement day on Cards (for example the 27th). An issuer "statement is ready" email on that day is this same first nudge, not an extra one. Send: "Statement ready for CIBC Visa-1001: forward or download it."
   - The second nudge is three days later, and only if that cycle's statement is still not imported. Send: "Statement should be out for CIBC Visa-1001."
   - Do not send on the day after the statement day, or the day after that. Do not send a third nudge.
3. Stop for that cycle once a statement whose statement date is in the current month is on the Statements sheet or named in that card's Statement file. The next cycle is the next month's statement day. Skip Chequing and Savings rows.
4. If nothing is ready and today is not a statement day or three days after one, send nothing.

The statements folder is `Family Book - {year}/statements/{Issuer Product}-{last4}/`. The file name is `YYYY-MM-DD statement.ext`, and the date is the statement date.

Made by SkybatanX (@SkyXFunNext).
