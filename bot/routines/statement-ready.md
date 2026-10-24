# Routine: Statement ready

- **Schedule:** daily, with the receipt scan (around 8:00 PM in the user's timezone). It can also run on its own at 9:00 AM if the scan is not created yet.
- **Create when:** the owner started the book, and Annual Summary `C47` is `on`. Do not create it at setup. A member does not send this nudge. If an older install already created it, leave the routine and follow the gate below.
- **Uses:** the daily mail scan and the Cards sheet. It does not log a purchase.

## Prompt

Read Annual Summary `C47` first. If it is `off`, blank, or missing, send nothing. Do not treat an issuer email as a statement nudge, and do not import a statement that arrived only by email.

Look for a statement-ready email, and look at the Cards sheet. Send one nudge per account, not per card. An authorized-user card, such as 1002 on the same account as 1001, does not get a second nudge. Use the primary card's label, for example `CIBC Visa-1001`.

1. During the daily scan, an email whose subject or first lines say the statement is ready (for example "Your CIBC Visa statement is ready") is this nudge, not a receipt. Match the issuer or the product to the account. Reply once: "Statement ready for CIBC Visa-1001: forward or download it." Use the real label. Say it in the language of this chat. Do not log the email as a purchase. Do not download a statement that the email does not attach. If the email has the PDF attached, save it with the statement-reader skill and import it. That import ends the nudge for this cycle.
2. Each account gets at most two nudges per cycle, then this routine stops until the next cycle. The cycle date is that account's statement day, not "the current month".
   - The first nudge is on the cycle date (for example the 27th). An issuer "statement is ready" email on that day is this same first nudge, not an extra one. Send: "Statement ready for CIBC Visa-1001: forward or download it."
   - The second nudge is three days after the cycle date, including when that day is in the next month. A statement day of 30 nudges again on the 3rd of the next month if that cycle is still missing. Send: "Statement should be out for CIBC Visa-1001."
   - Do not send on the day after the cycle date, or the day after that, unless that day is the cycle date plus three. Do not send a third nudge.
3. Stop for that cycle once a statement with that cycle's statement date is on the Statements sheet or named in that account's Statement file. Do not stop merely because some statement's month equals the current month. The next cycle is the next statement day. Skip Chequing and Savings rows.
4. If nothing is ready and today is not a cycle date or three days after one, send nothing.

The statements folder is `Family Book - {year}/statements/{Issuer Product}-{last4}/`. The file name is `YYYY-MM-DD statement.ext`, and the date is the statement date. Statement id is `{Issuer Product}-{last4}-{statement date}`.

Made by SkybatanX (@SkyXFunNext).
