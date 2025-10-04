# Property Hub

A Django test project by Devsinc for listing, searching, and managing real-estate properties. Users can register, publish listings, mark listings as favourites, and manage their profile.

---

## ✨ Key Features

- Property catalogue with rich details & images
- Favourite/Un-favourite listings (toggle button & personal favourites page)
- User authentication & profile management
- Django Admin for staff management
- REST-friendly URL structure & clean templates
- Docker-based production setup + UV for local development
- Tests with `pytest`

---

## 🗂 Project Layout

```text
Property-Hub/
├── apps/                 # Custom Django apps
│   ├── properties/       # Property listings domain
│   │   ├── models.py     # Property, Image, Feature, Favourite
│   │   ├── views.py      # List / Detail / Create / Update / ToggleFavourite
│   │   ├── urls.py       # URLConf for the app
│   │   └── templates/
│   └── users/            # Registration & profile domain
│       ├── models.py     # Using Django default User; extra helpers
│       ├── views.py      # Sign-up / Sign-in / Profile views
│       └── urls.py
│
├── config/               # Project-level settings & urls
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
│
├── templates/            # Global templates & base.html
├── staticfiles/          # Collected static assets for production
├── manage.py             # Django entry point
├── Dockerfile            # Production image definition
├── docker-compose.yml    # Local development stack (Django + DB + nginx)
├── Makefile              # Handy shortcuts (build / migrate / run / test …)
├── pyproject.toml & uv.lock
├── .env
└── README.md
```

---

## ⚙️ Local Development Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/anasengence/property-hub.git
   cd Property-Hub
   ```
2. **Create an `.env` file** (copy `.env.sample` if present) and adjust values:
   ```dotenv
   DJANGO_SECRET_KEY=changeme
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   DATABASE_URL=sqlite:///db.sqlite3
   AWS_ACCESS_KEY_ID=changeme
   AWS_SECRET_ACCESS_KEY=changeme
   AWS_STORAGE_BUCKET_NAME=changeme
   ```
3. **Install Python dependencies** via UV:
   ```bash
   make build       # installs UV & all packages
   ```
4. **Apply migrations & collect static:**
   ```bash
   make migrate
   ```
5. **Run the development server:**
   ```bash
   make run  # http://127.0.0.1:8000/
   ```
6. **Run tests:**
   ```bash
   make test
   ```

---

### 🐳 Docker (local deployment simulation)

Spin up the complete stack (Django, Localstack):

```bash
docker-compose up --build
```
Access the app at `http://localhost:8000`.

---

## 🔐 Environment Variables

| Variable            | Description                                   |
|---------------------|-----------------------------------------------|
| `DJANGO_SECRET_KEY` | Unique secret key for crypto signing          |
| `DATABASE_URL`      | Database DSN (SQLite recommended)             |
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID                             |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key                     |
| `AWS_STORAGE_BUCKET_NAME` | AWS S3 Bucket Name                      |
| `DEBUG`             | `True` for development, `False` in production |

---

## 📦 Useful Make Commands

| Command         | Action                               |
|-----------------|--------------------------------------|
| `make build`    | Install dependencies with UV          |
| `make migrate`  | Run migrations & collectstatic       |
| `make run`      | Start Django development server      |
| `make test`     | Run the test-suite with pytest       |
| `make shell`    | Open a Django shell                  |
