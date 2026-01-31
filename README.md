# Bookly — FastAPI Book Management Service

A production-oriented FastAPI project that demonstrates:
- User authentication (JWT), email verification, password reset
- Role-based access control (admin / user)
- Book CRUD with user ownership, reviews, and tag management
- Async SQLModel (SQLAlchemy) models and async DB session lifecycle
- Redis-based JWT blocklist (logout), Celery background tasks for emails (redmail)
- Tests with pytest

<img src="image.png" alt="JWT and Redis flow diagram">
<img src="image-1.png" alt="Database relationships (Book/User/Review)">

Table of contents
- Project highlights
- Tech stack
- Quickstart (install + run demo)
- Environment variables (.env.example)
- Running the full project (Celery, workers)
- Database & Redis
- Architecture & models (summary)
- API Reference
  - Demo endpoints (main.py)
  - Auth endpoints
  - Books endpoints
  - Reviews endpoints
  - Tags endpoints
- Testing
- Pushed On Docker Hub
- Contributing & Troubleshooting

---

## Project highlights
- Fully async FastAPI backend with modular design (auth, books, reviews, tags)
- Email sending via Celery + redmail (with fallback to background task)
- JWT refresh & access tokens, token revocation using Redis blocklist
- SQLModel models for typed schema and relationships
- Unit tests included (pytest)

---

## Tech stack
- Python 3.10+ (check requirements.txt)
- FastAPI
- SQLModel / SQLAlchemy (async)
- PostgreSQL (implied by sqlalchemy.dialects.postgresql usage)
- Redis (for token blocklist)
- Celery (background tasks)
- redmail (sends emails)
- pytest (tests)

See full dependency list in requirements.txt.

---

## Quickstart (local / demo)
This repository includes a small demo FastAPI app at `main.py` (quick to run) and a full application under `src/`.

1. Create and activate a virtual environment
   - macOS / Linux:
     - python -m venv .venv
     - source .venv/bin/activate
   - Windows:
     - python -m venv .venv
     - .venv\Scripts\activate

2. Install dependencies
   - pip install -r requirements.txt

3. Add environment variables (see `.env.example` below)

4. Run the demo app (simple example FastAPI in root)
   - uvicorn main:app --reload --port 8000
   - Visit http://127.0.0.1:8000/docs for the interactive Swagger UI of the demo app.

Notes:
- The demo app in `main.py` showcases basic FastAPI concepts and simple endpoints included for quick testing.
- The full application code is implemented under `src/`. To run the full app, create a small ASGI entrypoint that mounts the routers in `src` or extend `main.py` to import & include the routers from `src`.

---

## Environment variables (.env.example)
Create a `.env` file at the project root. The app reads configuration via `src/config.py`.

```
# Required
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE=60               # minutes (integer)
REFRESH_TOKEN_EXPIRE=7               # days (integer)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0

# Email (redmail / Gmail)
GMAIL=youremail@gmail.com
GMAIL_PASSWORD=your-gmail-password

# Public domain used to create verification/reset links
DOMAIN=localhost:8000
```

Important: store secrets (SECRET_KEY, GMAIL_PASSWORD) safely (don't commit to source control). For production, use a secrets manager.

---

## Running the full application (background tasks & Celery)

Celery is configured in `src/celerly.py` (note: file spelled `celerly.py`). The celery app object is `celery_app`.

Start a worker:
- celery -A src.celerly.celery_app worker --pool=solo -l info -E

Start Flower (monitor tasks):
- pip install flower
- celery -A src.celerly.celery_app flower --address=0.0.0.0 --port=5555 --loglevel=info

The app attempts to send mail via Celery. If Celery fails, it falls back to FastAPI BackgroundTasks to call redmail synchronously.

---

## Database & Redis
- DB initialization and async session is handled in `src/db/main.py`.
  - `init_db()` will run SQLModel.metadata.create_all.
  - `get_session()` yields an async SQLModel session (sessionmaker + AsyncSession) and uses `expire_on_commit=False`.
- Models are in `src/db/models.py`. PostgreSQL UUID and timestamp columns are used.
- Redis client for token blocklist is in `src/db/redis_client.py`.
  - JWT IDs (jti) are stored on logout for JTI_EXPIRY seconds (currently 3600).
  - When validating access tokens, the project checks Redis for revoked JTI.

Migrations: Alembic is listed in requirements. If you want schema migrations, create an Alembic configuration and migration scripts that reflect `src/db/models.py` (SQLModel/SQLAlchemy).

---

## Architecture & Models (summary)

Key models (from src/db/models.py):

- User
  - uid (UUID, PK), username, email, password_hash, role (user/admin), is_verified, created_at, updated_at
- Book
  - id (UUID, PK), title, author, year, isbn, pages, price, available, summary, user_uid (FK -> users.uid), created_at, updated_at
- Review
  - uid (UUID, PK), rating (int), review_txt, user_uid (FK -> users.uid), book_uid (FK -> books.id), created_at, updated_at
- Tag
  - uid (UUID, PK), name, created_at
- BookTag (association table)
  - book_id, tag_id (composite PK)

Relationships:
- Book -> reviews (1 -> many)
- User -> reviews (1 -> many)
- Book <-> Tag (many-to-many via BookTag)
- Book -> user (owner via user_uid)

---

## API Reference

The project contains:
- demo endpoints in `main.py` — for quick testing
- full application routers under `src`:
  - Auth router: `src/auth/auth_router.py`
  - Book router: `src/books/routes.py`
  - Review router: `src/reviews/review_routes.py`
  - Tag router: `src/tags/routes.py`

Router base paths are not enforced by a single ASGI entrypoint in the repo — when you create the app router mount points, use a consistent prefix such as `/api/v1/auth`, `/api/v1/books`, `/api/v1/reviews`, `/api/v1/tags`. Below I document endpoints as they appear in the code (you might need to prefix when mounting).

All examples use JSON and show required fields from Pydantic schemas in the repo.

---

### Demo endpoints (main.py)

- GET /
  - Description: simple hello world
  - Example:
    - curl http://127.0.0.1:8000/
    - Response: {"Hello": "World"}

- GET /greet/{name}
  - Params: path name (string)
  - Example: GET /greet/Alice
  - Response: {"greeting":"Hello, Alice!"}

- GET /greet_me?name=...
  - Query param: name (string)
  - Example: GET /greet_me?name=Tabarak
  - Response: {"greeting":"Hello, Tabarak!"}

- GET /sayhi?name=&age=
  - Query params: name (optional, defaults "user"), age (int)
  - Example: GET /sayhi?name=Sam&age=30
  - Response: {"message":"Hi,Sam! You are 30 years old."}

- POST /create_user
  - Body: JSON User model
  - Example body:
    {
      "name": "Tabarak",
      "age": 28,
      "address": "Somewhere"
    }
  - Response echoes the same object (Pydantic used)

- GET /getheader
  - Returns selected request headers (Accept, Content-Type, User-Agent, Host)

---

### Auth endpoints (src/auth/auth_router.py)
Mount path idea: /api/v1/auth

Pydantic schemas: see src/auth/schemas.py
- UserCreateModel: username, email (EmailStr), password
- UserLoginModel: email, password
- EmailSchema: addresses: list[str]
- PasswordResetSchema: email
- PasswordResetConfirmSchema: new_password, confirm_password

Important behaviors:
- Signup sends an email verification token (via Celery or background task)
- Login returns both access_token and refresh token (refresh token expiry is configured in env)
- Logout adds the token's jti to Redis blocklist
- Password reset uses a time-limited email token

Endpoints:

- POST /send_mail
  - Body: EmailSchema { "addresses": ["a@x.com", ...] }
  - Sends a test email via Celery; fallback to BackgroundTasks.
  - Response: {"message": "Email is being sent successfully"}

- POST /signup
  - Body: UserCreateModel
  - Response: {"verified": false, "message": "User created successfully. Please verify your email."}
  - Status: 201 Created (on success)
  - Example:
    curl -X POST http://localhost:8000/api/v1/auth/signup -H "Content-Type: application/json" \
      -d '{"username":"alice","email":"alice@example.com","password":"secret123"}'

- POST /login
  - Body: UserLoginModel
  - Response:
    {
      "message":"Login successful",
      "access_token":"<jwt>",
      "refreash_token":"<jwt>",
      "user":{"email":"alice@example.com","u_id":"<uuid>"}
    }

- GET /refresh_token
  - Use the refresh token Bearer to obtain new access token.
  - Returns: {"access_token": "<new_jwt>"}

- GET /me
  - Requires access token.
  - Returns current user details (depends on token payload and user service)

- GET /verify/{token}
  - Accepts email verification token created at signup.
  - Verifies the user in DB and returns verified status/message.

- POST /getverified
  - Query the user verification status by email (response model: UserModel)

- DELETE /delete_user?email=...
  - Deletes a user and related books/reviews. Returns message when deleted.

- GET /logout
  - Revokes access token by adding JTI to Redis blocklist. Response: {"message": "Logged Out"}

- POST /password_reset
  - Body: PasswordResetSchema {"email":"..."}
  - Sends password reset link via email (background task)
  - Response: {"message": "Password reset link has been sent to your email"}

- POST /reset_password/{token}
  - Body: PasswordResetConfirmSchema { "new_password": "...", "confirm_password": "..." }
  - Resets the password if token valid and passwords match.

Notes:
- The project uses `AccessTokenBearer` and `RefreshTokenBearer` custom classes (in `src/auth/dependencies.py`) to decode/validate tokens and handle role-based access.

---

### Books endpoints (src/books/routes.py)
Mount path idea: /api/v1/books

Pydantic schemas:
- BookCreateModel: title, author, year, isbn, pages, price, available, summary
- Book: response model includes id, created_at, updated_at etc.
- BookUpdate: partial updates

Endpoints:

- GET / (list all books)
  - Auth: requires access token; role user/admin
  - Response: list of Book objects

- GET /user/{u_id}
  - Returns all books submitted by a user (u_id is UUID string)

- POST /
  - Create a book (body: BookCreateModel)
  - Auth: access token required; the created book is associated with authenticated user
  - Response: created book (BookCreateModel in code returns created object)

- GET /{book_uid}
  - Retrieve book by UUID

- PATCH /{book_uid}
  - Body: BookUpdate
  - Returns updated Book

- DELETE /{book_uid}
  - Deletes the book (requires proper role & authorization) and returns message

Example create:
curl -X POST http://localhost:8000/api/v1/books \
  -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" \
  -d '{"title":"The Book","author":"Author","year":2020,"isbn":"12345","pages":200,"price":9.99,"available":true,"summary":"..."}'

---

### Reviews endpoints (src/reviews/review_routes.py)
Mount path idea: /api/v1/reviews

Schemas:
- ReviewCreateSchema, ReviewUpdateSchema, ReviewGetSchema in `src/reviews/schema.py`

Endpoints:

- GET /get_all_reviews
  - Public: returns all reviews

- GET /get_review_by_id/{review_id}
  - Get a single review by UID

- POST /add_review/{book_uid}
  - Body: ReviewCreateSchema
  - Auth: requires logged-in user (get_current_logged_user)
  - Creates a review for a book by the current user

- DELETE /delete_review/{review_id}
  - Delete a review by id (the route does not show explicit auth checks; adjust as required)

- PATCH /update_review/{review_id}
  - Update a review using ReviewUpdateSchema

---

### Tags endpoints (src/tags/routes.py)
Mount path idea: /api/v1/tags

Schemas:
- TagCreateSchema { name: str }
- TagAddSchema { tags: [TagCreateSchema] }
- TagSchema (response)

Endpoints:

- GET / - list all tags (requires role user/admin)
- POST / - create a single tag (requires role user/admin)
- POST /book/{book_uid}/tags - add tags to a book (requires role user/admin)
- PUT /{tag_uid} - update a tag
- DELETE /{tag_uid} - delete a tag (204 No Content on success)

---

## Example flows

1) Signup + verify + login
- Signup:
  curl -X POST http://localhost:8000/api/v1/auth/signup \
    -H "Content-Type: application/json" \
    -d '{"username":"alice","email":"alice@example.com","password":"secret123"}'

- Check email (in dev you may see logs or use redmail saved messages). Use /verify/{token} with the emailed token to verify.

- Login:
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"alice@example.com","password":"secret123"}'

2) Use access token to create book:
  curl -X POST http://localhost:8000/api/v1/books \
    -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" \
    -d '{"title":"Title","author":"Author","year":2023,"isbn":"1111","pages":100,"price":9.99,"available":true,"summary":"..."}'

3) Logout (revokes access token)
  curl -X GET http://localhost:8000/api/v1/auth/logout \
    -H "Authorization: Bearer <access_token>"

---

## Testing
- Run tests:
  - pytest -q
- Tests are located in `src/tests/` (conftest, test_auth.py, test_books.py). Ensure the test DB and env are configured before running.

---
## Pushed On Docker Hub
This backend is also dockerize and pushed on `docker hub` you can also check out the image [here](https://hub.docker.com/r/tabarakallah/bookly) 

## Troubleshooting & notes
- If email delivery fails in dev, Celery fallback uses FastAPI BackgroundTasks which calls redmail synchronously.
- Redis must be reachable at REDIS_URL for token revocation to work.
- Database migrations are not included — consider adding Alembic config for production migrations.
- The code uses async SQLModel + asyncpg — ensure DATABASE_URL uses the `postgresql+asyncpg://` driver.

---

## Contributing
- Open issues / PRs are welcome.
- Guidelines:
  - Add tests for new functionality in `src/tests/`
  - Keep environment secrets out of commits
  - For schema changes, add or update migration scripts (Alembic recommended)

---

## Contact
- Repo owner: TabarakAllahKhan
- Use repository issues for bugs, feature requests, or questions.

