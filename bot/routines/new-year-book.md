# Routine: New year's book

- **Schedule:** every December 20 at 9:00 AM in the user's timezone.
- **Create when:** this bot started the book (role `owner`). Do not create this routine for a bot that joined an existing book.
- **Uses:** the `family-book` skill (sections 0, 1, 1a, and 1b).

## Prompt

Create next year's Family Book with the family-book skill. Let YYYY be next year. Reply in the language the user writes in this chat, or the Grok Bot app or system language when nobody has just written.

If memory says this bot joined the book (member) rather than starting it, do not create a workbook and do not upload a template. Follow section 1b: look for the owner's `Family Book - YYYY`, save the new folder id, workbook id, and receipts folder id, tell the user in one or two lines that you linked it, and stop. If it is not shared with you yet, say that you are waiting for the owner and stop.

Owner steps:

1. Check this repo for a newer skill first. Download `https://raw.githubusercontent.com/Skybatan/family-book/main/bot/skills/family-book/SKILL.md`. If its body differs from the installed family-book skill, save the new body over it (keep the name and description). If GitHub can't be reached, continue with the installed skill.
2. If a `Family Book - YYYY` book already exists in the user's storage, skip creating another. Tell the user that next year's book is already there, and stop.
3. Download a fresh template from `https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx`, verify it opens with openpyxl (sheets include Annual Summary, Jan to Dec, Holidays, and a hidden Log), and refresh the copy in `Family Book - Templates`. If the download fails, use the copy already in `Family Book - Templates`.
4. Build the workbook as the skill describes: year in Annual Summary `F5`, the user's currency from memory, uploaded as a Google Sheet or an .xlsx on OneDrive. Read it back and confirm Jan 1 shows the right weekday. Confirm the hidden Log tab is present (section 3b). On OneDrive, re-download right before this write and upload immediately.
5. Fill the Holidays tab with next year's public holidays for the user's holiday region from memory. Write the holiday descriptions in the language you are using for this chat. Offer to carry over their anniversaries and birthdays from this year's book.
6. Save the new folder id, workbook id, and receipts folder id to memory as next year's book. Keep using this year's book for receipts dated this year. Remind the owner in one line to share the new `Family Book - YYYY` folder with the same family members, as editors. Do not invite anyone yourself. Their bots will attach; they do not each create a book.

Then tell the user in this Grok Bot chat, in two or three lines: the new book is ready (with a link if available), the holidays that were filled in, and whether the template version changed. If anything failed, say what and what you need from them. Sheet names, category labels, and receipt file names stay English.
