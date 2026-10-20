# Routine: Daily receipt scan

- **Schedule:** daily, around 8:00 PM in the user's timezone.
- **Create when:** the user chose at least one email inbox (Gmail or Outlook) at setup.
- **Uses:** the `family-book` skill (sections 3, 3a, and 4).

## Prompt

Run the family-book skill's email scan for the user's household Family Book. Scan every inbox the user chose at setup (Gmail or Outlook) for new order confirmations, receipts, and invoices since the last scan (Amazon, Costco, Home Depot, Walmart, and any other merchants). On the very first run, cover the last 30 days and mention, in their language, that older receipts from this year can be backfilled on request. Skip shipping or delivery notices, marketing, and anything already in the dedupe log. Log each new purchase into the current year's Family Book (Google Sheet or Excel workbook; ids are in memory) on the right month sheet, day, and category, splitting multi-category receipts as the skill describes.

Every email receipt MUST also be saved as a file in that year's receipts folder (ids in memory), following the skill's section 3a: the PDF attachment if there is one, otherwise the email rendered as a PDF or a one-page PNG, named "YYYY-MM-DD Merchant Total.ext". Check the file shows the merchant, date, and total before uploading. Only add an email to the dedupe log after its file is saved. Also check that receipts already in the dedupe log have a file in the receipts folder, and save any that are missing. This is read-only for email: never reply, forward, send, label, or delete anything.

Report to the user in this Grok Bot chat, in their chosen language, with a short digest of what was logged (merchant, date, total, category, saved file) and anything unclear that needs their call. Item notes written into the book are in that language too. Receipt file names stay `YYYY-MM-DD Merchant Total.ext`. If nothing new was found, send nothing.
