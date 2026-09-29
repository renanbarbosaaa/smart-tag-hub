# Smart Tag Hub

A small backend service that redirects short links, built for NFC tags. Write one short link on a tag once, then change where it points whenever you want.

Read this in Portuguese: [README- PT BR.md](ReadMe-PTBR.md)

## What is it?

Smart Tag Hub is a link redirection service. The NFC tag stores only a short link. When someone taps the tag with a phone, the service finds the real destination and sends the person there, very fast.

## Why I built it

I sell NFC cards that send people to places like a Google review page, an Instagram profile, a WhatsApp chat or a landing page.

I wanted a system of my own for three reasons:

- I do not want to depend on platforms owned by other people.
- NFC chips have very little memory. Saving only a short link leaves the chip space free.
- Customers often ask to change the destination later. With a normal tag, that means rewriting the chip. With this service, I only change the destination in my system and the card keeps working.

## How it works

1. A short link is written on the NFC tag once.
2. A person taps the tag with their phone.
3. The service looks up the short link and sends the phone to the current destination.
4. When a customer wants a new destination, only the stored destination changes. The tag stays exactly the same.

## Features

- Create short links for any valid web address.
- Fast redirect to the current destination.
- Temporary redirects on purpose, so browsers do not remember old destinations.
- Input validation for short links and destination addresses.
- Clear error messages for unknown or badly formatted links.
- Automated test suite.

## Tech stack

- Python
- FastAPI
- SQLAlchemy (async)
- SQLite for local development
- pytest and httpx for testing

## Architecture

The project follows a simplified Clean Architecture, split into layers with clear responsibilities:

| Layer | Responsibility |
| --- | --- |
| `api` | Receives web requests and returns responses. |
| `domain` | Business rules and validations. It knows nothing about the database. |
| `infrastructure` | Talks to the database and implements what the domain asks for. |
| `tests` | Automated tests for the rules and for the full flow. |

Because the domain does not depend on the database, the storage can change later without rewriting the business rules.

## Running locally

You need Python 3.11 or newer.

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
pytest
uvicorn api.main:app --reload
```

## Project status

- Done: the core backend is complete and covered by automated tests.
- Next: a production-ready database.
- Next: an admin dashboard (front end) to view and manage all links in one place.

## Author

Renan Barbosa - [GitHub](https://github.com/renanbarbosaaa)