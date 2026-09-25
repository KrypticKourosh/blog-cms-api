# Blog CMS (Content Management System) API

A **RESTful API** built with **Django's REST Framework** for blogging with user authentication, post management, 
 engagement features (likes, comments, views), and full API documentation.

## Features

- Blog posts with **comments, likes, views, tags, and categories**
- **JWT** authentication (register, login, token refresh, logout)
- Image uploads for posts
- Ownership-based permissions (authors can only edit/delete their own posts)
- **OpenAPI** documentation with **Swagger UI**
- **Docker** and **PostgreSQL** support
- **pytest** for testing
- Rate limiting and throttling
    
## Built with

- Django 6.x
- Django REST Framework
- djangorestframework-simplejwt
- drf-spectacular (for Swagger)
- django-filter
- PostgreSQL
- Docker & Docker Compose
- pytest + factory_boy

(See requirements.txt for exact versions.)

## Getting Started

Clone the repo:
```bash
git clone https://github.com/KrypticKourosh/blog-cms-api/
cd blog-cms-api
```

### Option 1: Docker (Recommended)

```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY

docker compose up --build
```

In another terminal:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### Option 2: Local Development

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API docs

After running the server check out http://localhost:8000/api/docs/ for SwaggerUI:

<img width="1825" height="805" alt="SwaggerUI" src="https://github.com/user-attachments/assets/258e0599-f23d-4f40-940e-a8abe9429514" />

**Note:** POST, PUT, PATCH and DELETE endpoints require authentication. 
Start by registering and logging in using the endpoints in the **auth** tab of Swagger.

## API Overview

| Endpoint                              | Method              | Description                        | Auth Required          |
|---------------------------------------|---------------------|------------------------------------|------------------------|
| `/api/auth/register/`                 | POST                | Register a new user                | No                     |
| `/api/auth/login/`                    | POST                | Obtain JWT tokens                  | No                     |
| `/api/auth/token/refresh/`            | POST                | Refresh access token               | No                     |
| `/api/auth/logout/`                   | POST                | Blacklist refresh token            | Yes                    |
| `/api/auth/profile/`                  | GET / PATCH         | Retrieve or update own profile     | Yes                    |
| `/api/posts/`                         | GET / POST          | List / Create posts                | Read: No / Write: Yes  |
| `/api/posts/{slug}/`                  | GET / PATCH / DELETE| Retrieve / Update / Delete post    | Varies                 |
| `/api/posts/{slug}/publish/`          | POST                | Publish a draft post               | Author only            |
| `/api/posts/{slug}/like/`             | POST                | Like a post                        | Yes                    |
| `/api/posts/{slug}/unlike/`           | POST                | Unlike a post                      | Yes                    |
| `/api/posts/{slug}/comments/`         | GET / POST          | List / Create comments on a post   | Read: No / Write: Yes  |
| `/api/comments/{id}/`                 | GET / PATCH / DELETE| Retrieve / Update / Delete comment | Varies                 |
| `/api/categories/`                    | GET                 | List categories                    | No                     |
| `/api/tags/`                          | GET                 | List tags                          | No                     |
| `/api/docs/`                          | GET                 | Swagger UI                         | No                     |


## Tests
Run tests using:
```bash
pytest
```

or with Docker:
```bash
docker compose exec web pytest
```
A task failed? no problem, open an issue.

## Future Improvements

- Redis and Celery
- CI/CD with GitHub Actions
- Login with Google account
