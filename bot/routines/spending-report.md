# Routine: Spending report

- **Schedule:** daily, around 8:00 PM in the user's timezone. Most days it sends nothing.
- **Create when:** this bot writes to a Family Book, owner or member. Create it at setup. It does not wait for a statement.
- **Uses:** the workbook's daily amount cells. It does not log a purchase and it does not change an amount. On a local book it reads the file with `bot/local/bookio.py` (`report_totals`, `advice`, `week_period`, `report_already_sent`, `record_report_sent`). It does not open Excel.

## Prompt

Read Annual Summary `C49` (last weekly report), `C50` (last monthly report), and `C51` (last yearly report). Download `https://raw.githubusercontent.com/Skybatan/family-book/main/bot/local/bookio.py` if the report helpers are not on the box. Category totals are the sum of the amount cells in each category for that date range. Dates come from the year in `F5` and the month sheet. Do not ask Excel, Numbers, or LibreOffice to calculate.

A local book is read by copying the `.xlsx` to the bot (one local-tool approval) and running the report there. If the registered computer is off, asleep, or the file is locked, send nothing and do not record the period. The next run tries again. Do not send a report from a copy that is older than the file on the computer.

Send only a period whose id is not already in `C49`, `C50`, or `C51`. Record the id in that cell after the message is sent, in one write that does not touch amount cells. A second run with the same id sends nothing.

- **Weekly.** The period is the Monday-to-Sunday week ending on the most recent Sunday, including today when today is Sunday. The id is that Sunday as `YYYY-MM-DD`. Send the categories that have spending, the total, and one advice sentence: the largest category, its amount, the week's total, and its share. If every category is zero, send nothing and still record the id so a later empty week does not retry all evening.
- **Monthly.** On the 1st, or on the first later day the book can be read, send the previous calendar month. The id is `YYYY-MM`. Same shape as the weekly report.
- **Yearly.** On January 1, or the first later day the book can be read, send the previous year. The id is that year. Same shape.

Say it in the language of this chat, or the Grok Bot app or system language when nobody has just written. Keep the category names in English, as the sheet labels them. Do not suggest a statement in this routine. The daily receipt scan is the only place that suggestion is sent, and only while `C48` is `not yet`.

Made by SkybatanX (@SkyXFunNext).
