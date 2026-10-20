# Routine: New year's book

- **Schedule:** yearly, around December 20, in the user's timezone.
- **Uses:** the `family-book` skill (sections 0, 1, and 1a).

## Prompt

Create next year's Family Book with the family-book skill. Let YYYY be next year. If a `Family Book - YYYY` book already exists in the user's storage, do not create another; just check it is complete. Otherwise:

1. Create the folder `Family Book - YYYY` in the user's storage (Google Drive or OneDrive, as saved in memory) with a `receipts` subfolder inside it.
2. Get the latest template: download it from https://raw.githubusercontent.com/Skybatan/family-book/main/template/family-book-template.xlsx, verify it opens with openpyxl, and refresh the copy in `Family Book - Templates`. If the download fails, use the copy already in `Family Book - Templates`.
3. Build the workbook as the skill describes: year in Annual Summary `F5`, the user's currency from memory, uploaded as a Google Sheet or an .xlsx on OneDrive. Read it back and confirm Jan 1 shows the right weekday.
4. Fill the Holidays tab with next year's public holidays for the user's holiday region from memory. Offer to carry over their anniversaries and birthdays from this year's book.
5. Save the new folder id, workbook id, and receipts folder id to memory as next year's book. Keep using this year's book for receipts dated this year.

Then tell the user in this Grok Bot chat, in two or three lines: the new book is ready (with a link if available), the holidays that were filled in, and whether the template version changed. If anything failed, say what and what you need from them.
