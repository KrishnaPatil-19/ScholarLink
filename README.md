# ScholarLink

ScholarLink is a Django-based academic discussion platform where users can create topic-based rooms, join conversations, reply in threads, vote on messages, and manage their profiles. The project also includes a small REST API for room data and optional Google sign-in using `django-allauth`.

## Features

- Custom user model with email-based authentication
- User registration, login, logout, and profile update
- Topic-based discussion rooms
- Create, update, and delete rooms
- Post messages and threaded replies inside rooms
- Upvote and downvote discussion messages
- Room participants and activity feed
- Search rooms by topic, title, or description
- REST API endpoints for room data
- Google OAuth login support through `django-allauth`

## Tech Stack

- Python 3.13
- Django 6
- Django REST Framework
- django-allauth
- django-cors-headers
- SQLite
- Pillow

## Project Structure

```text
scholarlink/
|-- base/                 # Main Django app: models, views, forms, API
|-- scholarlink/          # Project settings and root URL configuration
|-- static/               # CSS, JS, images
|-- templates/            # Shared project templates
|-- manage.py
|-- db.sqlite3
|-- convert_md_to_pdf.py  # Utility script included in the project
```

## Core Models

- `User`: custom authentication model using email as the login field
- `Topic`: category used to organize rooms
- `Room`: discussion space with host, topic, description, and participants
- `Message`: room message with threaded replies and voting support

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd scholarlink
```

### 2. Create and activate a virtual environment

Windows:

```powershell
python -m venv denv
.\denv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv denv
source denv/bin/activate
```

### 3. Install dependencies

This project currently uses the following main packages:

```bash
pip install Django djangorestframework django-cors-headers django-allauth pillow
```

If you want to preserve the exact environment used during development, create a `requirements.txt` from the active virtual environment and install from that file.

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## API Endpoints

The project exposes a few basic REST endpoints:

```text
GET /api/
GET /api/rooms/
GET /api/rooms/<id>/
```

## Authentication Notes

- The project uses a custom `User` model defined in `base.models`.
- Email is used as the primary login field.
- Session-based authentication is enabled.
- Google login is configured through `django-allauth`, but you must add your own Google OAuth credentials before using it in a deployed setup.

## Static and Media Files

- Static files are served from `static/`
- Uploaded avatars are stored under `static/images/`
- Media URL is configured as `/images/`

## Development Notes

- Database: SQLite (`db.sqlite3`)
- CORS is currently open to all origins for development
- `DEBUG` is enabled in settings
- `manage.py check` passes with no issues in the current project state

## Suggested Improvements

- Add a `requirements.txt` file
- Move sensitive settings such as `SECRET_KEY` to environment variables
- Restrict CORS and production settings before deployment
- Add tests for views, forms, and API endpoints
- Separate media uploads from static assets in production

## License

This project is available for academic and learning purposes. Add a license file if you plan to publish it publicly on GitHub.
