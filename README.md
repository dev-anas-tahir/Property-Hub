# Property Hub

A modern Django application for listing, searching, and managing real-estate properties. Built with a component-based architecture using Django Unicorn for reactive, interactive user experiences without full page reloads.

---

## ✨ Key Features

- **Component-Based Architecture**: Built with Django Unicorn for reactive, interactive components
- **Real-Time Interactions**: Favorite properties, paginate, and filter without page reloads
- **Property Management**: Create, edit, and delete property listings with image galleries
- **Interactive Forms**: Real-time validation and feedback on all forms
- **User Authentication**: Complete auth flow with signup, login, profile, and password management
- **Responsive Design**: Bootstrap 5-based UI that works on all devices
- **Image Carousel**: Interactive image galleries with keyboard navigation
- **Favorites System**: Toggle favorites with instant UI updates
- **Django Admin**: Full admin interface for staff management
- **Docker Support**: Production-ready Docker setup
- **Comprehensive Tests**: Test suite with pytest

---

## 🏗 Architecture

This project uses a **component-based architecture** powered by [Django Unicorn](https://www.django-unicorn.com/), enabling reactive, interactive user interfaces without writing JavaScript.

### Component-Based Design

All interactive features are built as reusable Unicorn components:

- **Shared Components**: Pagination, alerts, form fields, loading spinners
- **Property Components**: Property lists, cards, details, forms, image carousels
- **User Components**: Login, signup, profile, and password change forms

Components handle their own state, validation, and server communication, making the codebase modular and maintainable.

### Benefits

- **No Page Reloads**: All interactions happen seamlessly without full page refreshes
- **Real-Time Validation**: Forms validate as you type with instant feedback
- **Reusable Components**: Build once, use everywhere
- **Server-Side Logic**: All business logic stays in Python (no JavaScript required)
- **Progressive Enhancement**: Works with JavaScript, degrades gracefully without it

## 🗂 Project Layout

```text
Property-Hub/
├── apps/                      # Custom Django apps
│   ├── properties/            # Property listings domain
│   │   ├── components/        # Unicorn components
│   │   │   ├── property_list.py      # Paginated property listing
│   │   │   ├── property_card.py      # Property card display
│   │   │   ├── property_detail.py    # Property detail view
│   │   │   ├── property_form.py      # Create/edit form
│   │   │   ├── favorite_button.py    # Favorite toggle
│   │   │   ├── image_carousel.py     # Image gallery
│   │   │   └── delete_modal.py       # Delete confirmation
│   │   ├── models.py          # Property, PropertyImage, Favourite
│   │   ├── views.py           # Simple template views
│   │   ├── urls.py            # URLConf for the app
│   │   └── templates/
│   ├── users/                 # User authentication domain
│   │   ├── components/        # Unicorn components
│   │   │   ├── login_form.py         # Login form
│   │   │   ├── signup_form.py        # Registration form
│   │   │   ├── profile_form.py       # Profile editor
│   │   │   ├── password_change_form.py  # Password change
│   │   │   └── password_input.py     # Password field with toggle
│   │   ├── models.py          # User model extensions
│   │   ├── views.py           # Simple template views
│   │   └── urls.py
│   └── shared/                # Shared/reusable components
│       └── components/
│           ├── pagination.py         # Pagination component
│           ├── alert_message.py      # Toast/alert messages
│           ├── form_field.py         # Form field wrapper
│           └── loading_spinner.py    # Loading indicators
│
├── config/                    # Project-level settings & urls
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
│
├── templates/                 # Global templates & base.html
│   └── unicorn/               # Component templates
├── staticfiles/               # Collected static assets
├── manage.py                  # Django entry point
├── Dockerfile                 # Production image definition
├── docker-compose.yml         # Development stack
├── Makefile                   # Handy shortcuts
├── pyproject.toml & uv.lock   # Dependencies
├── COMPONENTS.md              # Component documentation
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

## 🧩 Django Unicorn Components

This project leverages Django Unicorn for all interactive features. Components are self-contained Python classes that handle:

- State management
- User interactions
- Form validation
- Database operations
- Event communication

### Key Components

**Property Components:**
- `property_list`: Paginated property listing with filtering
- `property_card`: Individual property display card
- `property_detail`: Full property details with actions
- `property_form`: Create/edit property with real-time validation
- `favorite_button`: Toggle favorite status
- `image_carousel`: Interactive image gallery

**User Components:**
- `login_form`: User authentication
- `signup_form`: User registration with validation
- `profile_form`: Profile editing
- `password_change_form`: Password management

**Shared Components:**
- `pagination`: Reusable pagination
- `alert_message`: Toast notifications
- `form_field`: Form field wrapper with errors
- `loading_spinner`: Loading indicators

For detailed component documentation, see [COMPONENTS.md](COMPONENTS.md).

### Component Usage Example

```html
<!-- In your template -->
{% load unicorn %}

<!-- Property list with pagination -->
{% unicorn 'property_list' %}

<!-- Favorite button -->
{% unicorn 'favorite_button' property_id=property.id %}

<!-- Alert messages -->
{% unicorn 'alert_message' %}
```

```python
# In your component (apps/properties/components/property_list.py)
from django_unicorn.components import UnicornView

class PropertyListView(UnicornView):
    properties: list = []
    current_page: int = 1
    
    def mount(self):
        self.load_properties()
    
    def load_properties(self):
        # Load and display properties
        pass
    
    def next_page(self):
        self.current_page += 1
        self.load_properties()
```

---

## 📦 Useful Make Commands

| Command         | Action                               |
|-----------------|--------------------------------------|
| `make build`    | Install dependencies with UV          |
| `make migrate`  | Run migrations & collectstatic       |
| `make run`      | Start Django development server      |
| `make test`     | Run the test-suite with pytest       |
| `make shell`    | Open a Django shell                  |

---

## 🧪 Testing

The project includes comprehensive tests for all components and functionality:

```bash
# Run all tests
make test

# Run specific test file
pytest apps/properties/tests/test_components.py

# Run with coverage
pytest --cov=apps
```

Test coverage includes:
- Component functionality
- Form validation
- User authentication flows
- Property CRUD operations
- Favorite system
- Image uploads
- End-to-end user flows

---

## 📚 Additional Documentation

- **[COMPONENTS.md](COMPONENTS.md)**: Comprehensive component reference with usage examples
- **[Django Unicorn Docs](https://www.django-unicorn.com/)**: Official Django Unicorn documentation
- **[Bootstrap 5 Docs](https://getbootstrap.com/docs/5.0/)**: UI framework documentation

---

## 🚀 Deployment

The project is production-ready with Docker support:

```bash
# Build production image
docker build -t property-hub .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up
```

Environment variables for production:
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Use PostgreSQL instead of SQLite
- Configure AWS S3 for media storage
- Set secure `DJANGO_SECRET_KEY`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📝 License

This project is for educational and demonstration purposes.
