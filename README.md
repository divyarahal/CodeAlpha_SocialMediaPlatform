# Connectly – Mini Social Media Platform

CodeAlpha Full Stack Development Internship – **Task 2**.
A small social network built with **Django** (backend), **SQLite** (database) and plain **HTML / CSS / JavaScript** (frontend).

## Features
- **User profiles** – sign up / log in / log out, bio and location, profile page with post, follower and following counts
- **Posts & comments** – create and delete posts (280 chars), comment on any post, paginated feeds
- **Like / follow system** – like and unlike posts, follow and unfollow users (updated instantly with JavaScript `fetch`, no page reload)
- **Feeds & discovery** – "Following" feed and "Everyone" feed, People page with search

## Database models
| Model | Fields |
|---|---|
| User (Django built-in) | username, password, … |
| Profile | user (1-1), bio, location |
| Post | author, content, created_at, likes (many-to-many with User) |
| Comment | post, author, content, created_at |
| Follow | follower, following, created_at (unique pair, no self-follow) |

## Run locally (Windows / VS Code)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo        # optional: demo users alice / bob / carol, password demo12345
python manage.py createsuperuser  # optional: for /admin
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Run tests
```bash
python manage.py test
```

## Project structure
```
socialsite/        project settings and root URLs
network/           the app: models, views, forms, urls, tests
  templates/       base, home, profile, post detail, people, login, signup
  static/network/  style.css, app.js (like / follow via fetch + CSRF)
  management/commands/seed_demo.py
```

## Main URLs
`/` feed · `/people/` · `/u/<username>/` profile · `/post/<id>/` post + comments · `/accounts/login/` · `/signup/` · `/admin/`
