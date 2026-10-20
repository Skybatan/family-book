# Routine: New year's book

- **Schedule:** every December 20 at 9:00 AM in the user's timezone.
- **Uses:** the `family-book` skill (sections 0, 1, and 1a).

## Prompt

Create next year's Family Book with the family-book skill. Let YYYY be next year.

1. Check this repo for a newer skill first. Download `https://raw.githubusercontent.com/Skybatan/family-book/main/bot/skills/family-book/SKILL.md`. If its body differs from the installed family-book skill, save the new body over it (keep the name and description). If GitHub can't be reached, continue with the installed skill.
2. If a `Family Book - YYYY` book already exists in the user's storage, skip creating another. Tell the user, in their language, that next year's book is already there, and stop.
3. Download a fresh template from `https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx`, verify it opens with openpyxl, and refresh the copy in `Family Book - Templates`. If the download fails, use the copy already in `Family Book - Templates`.
4. Build the workbook as the skill describes: year in Annual Summary `F5`, the user's currency from memory, uploaded as a Google Sheet or an .xlsx on OneDrive. Read it back and confirm Jan 1 shows the right weekday.
5. Fill the Holidays tab with next year's public holidays for the user's holiday region from memory. Write the holiday descriptions in the user's language. Offer to carry over their anniversaries and birthdays from this year's book.
6. Save the new folder id, workbook id, and receipts folder id to memory as next year's book. Keep using this year's book for receipts dated this year.

Then tell the user in this Grok Bot chat, in their chosen language, in two or three lines: the new book is ready (with a link if available), the holidays that were filled in, and whether the template version changed. If anything failed, say what and what you need from them. Sheet names, category labels, and receipt file names stay English.
