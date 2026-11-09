# AI Lead Hunter

An automated n8n workflow that finds potential clients for a web design studio.

Every day the system searches for local businesses in Ukraine through the
Google Places API, identifies companies without a proper website, checks for
duplicates, sends the candidates to AI qualification, and delivers the selected
leads to Telegram.

## Main Stages

- **Search Generation** — builds combinations of cities, categories and search
  modifiers. Queries rotate from day to day so the whole list is covered
  gradually.
- **Google Places** — fetches the business name, address, phone, rating,
  reviews, website and other details.
- **Filtering** — drops closed businesses, duplicates and companies that
  already have a proper website.
- **Memory** — a Data Table stores every business found so far, so the same
  business never shows up in a report twice.
- **AI Qualification** — OpenAI assesses each lead's potential, decides whether
  it needs a website, and produces a `lead_score`, a reason and a recommended
  website type.
- **Fallback** — if the AI is unavailable or returns an invalid response, a
  backup scoring algorithm is used.
- **Telegram** — a structured report with the new leads is built and sent to
  Telegram.

## Technologies

- n8n
- JavaScript
- Google Places API
- OpenAI API
- n8n Data Tables
- Telegram Bot API

## Project Goal

Automate finding and pre-qualifying potential clients instead of collecting
leads by hand.

## Files

```
workflow.json   the workflow, ready to import into n8n
sanitize.py     strips instance-specific data out of an n8n export
```

## Setup

1. Import `workflow.json` into an empty workflow in n8n.
2. Create three credentials and select them on the nodes that need them:
   Header Auth with `X-Goog-Api-Key` for Google Places, the OpenAI credential,
   and a Telegram bot token.
3. Create a Data Table named `lead_hunter_memory` and select it in
   **Get Known Businesses** and **Save New Leads**.
4. Put your Telegram chat id into `telegramChatId` in the **Config** node.
5. Run **Manual Test Run** once with `testMode: true` before switching the
   schedule on.

The export carries no credentials, no chat id and no data table id. Those are
yours to fill in after the import, which is why the dropdowns come in empty.
`sanitize.py` is what removes them, so the file stays safe to share after every
re-export:

```bash
python sanitize.py workflow.json
```
