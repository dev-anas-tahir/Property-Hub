# Property Hub

A modern real-estate property management platform built with Django, featuring a component-based architecture for listing, searching, and managing properties.

---

## 🛠 Tech Stack

### Backend
- **Django 6.0.1** - Web framework
- **Python 3.13+** - Programming language
- **PostgreSQL-17** - Database
- **UV** - Package manager

### Frontend
- **Tailwind CSS** - Utility-first CSS framework
- **DaisyUI** - Component library
- **HTMX** - Dynamic interactions
- **Alpine.js** - Lightweight JavaScript framework

### Infrastructure
- **Docker** - Containerization
- **AWS S3** - Media storage
- **Localstack** - Local AWS simulation

---

## 🏗 Architecture

### Project Structure

```
Property-Hub/
├── apps/
│   ├── properties/          # Property management
│   │   ├── models.py        # Property, PropertyImage models
│   │   ├── views.py         # View logic
│   │   ├── forms.py         # Form definitions
│   │   └── urls.py          # URL routing
│   ├── users/               # User authentication
│   │   ├── models.py        # User model
│   │   ├── views.py         # Auth views
│   │   └── forms.py         # Auth forms
│   └── shared/              # Shared utilities
│
├── config/                  # Project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL config
│   └── wsgi.py              # WSGI config
│
├── templates/               # HTML templates
│   ├── _layouts/            # Base layouts
│   ├── _components/         # Reusable components
│   ├── properties/          # Property templates
│   └── users/               # User templates
│
├── static/                  # Static assets
│   ├── src/                 # Source CSS
│   └── dist/                # Compiled CSS
│
├── staticfiles/             # Collected static files
├── media/                   # User uploads
├── Dockerfile               # Docker image
├── docker-compose.*.yml     # Docker compose configs
├── tailwind.config.js       # Tailwind configuration
├── pyproject.toml           # Python dependencies
└── justfile                 # Development commands
```

### Design Patterns

**Component-Based Templates**
- Reusable UI components in `templates/_components/`
- Separation of layouts, components, and pages
- DRY principle for forms, navigation, and UI elements

**App-Based Organization**
- Domain-driven design with separate apps
- Clear separation of concerns
- Modular and maintainable codebase

**Modern Frontend Stack**
- Utility-first CSS with Tailwind
- Progressive enhancement with HTMX
- Minimal JavaScript with Alpine.js
- Components from DaisyUI

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Node.js 18+ (for Tailwind CSS)
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Property-Hub
   ```

2. **Set up environment variables**
   ```bash
   cp .env.sample .env.dev
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   # Install Python and Node dependencies
   just build
   ```

4. **Run all the dev services in Docker**
   ```bash
   # Start all services PostgresDB, Redis, Mailhog and Localstack
   just up
   ```

5. **Run database migrations**
   ```bash
   just migrate
   ```

6. **Start development server**
   ```bash
   just runserver
   ```

7. **Access the application**
   ```
   http://127.0.0.1:8000
```

---

## 🔧 Development Commands

### Just Commands

| Command | Description |
|---------|-------------|
| `just build` | Install Python and Node dependencies |
| `just migrate` | Apply Django migrations |
| `just makemigrations` | Create new Django migrations |
| `just runserver [port]` | Start Django development server (default port: 8000) |
| `just up` | Start development services i.e (PostgresDB, Redis, Localstack and Mailhog) with Docker |
| `just down` | Stop development services |
| `just help` | Show all available commands |

### NPM Commands

| Command | Description |
|---------|-------------|
| `npm run build-css` | Build Tailwind CSS (watch mode) |
| `npm run build-css-prod` | Build Tailwind CSS (production) |

---

## 🔐 Environment Configuration

Your `.env` file will have the following variables:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DATABASE_URL=sqlite:///db.sqlite3

# AWS S3 (Localstack for local deelopment)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

---

## 🎨 Frontend Development

### Tailwind CSS

The project uses Tailwind CSS with DaisyUI for styling. Custom configuration is in `tailwind.config.js`.

**Adding new styles:**
1. Add Tailwind classes to your templates
2. Run `npm run build-css` to compile
3. Run `python manage.py collectstatic` to collect files

**Custom theme:**
- Primary color: Indigo (#6366f1)
- Secondary color: Purple (#d946ef)
- Accent color: Orange (#f97316)

### Component Development

Components are located in `templates/_components/`:
- `forms/` - Form inputs and controls
- `navigation/` - Navbar and footer
- `properties/` - Property-specific components
- `ui/` - General UI components

---

## 🧪 Testing

In Progress

---

## 📦 Deployment

### Production Build

```bash
# Build Docker image
docker build -t property-hub .

# Run with production compose
docker-compose -f docker-compose.prod.yml up
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set secure `DJANGO_SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Configure static file serving
- [ ] Set up monitoring and logging

---

## 🤝 Contributing

### Getting Started

1. Fork the repository
2. Create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Follow the code style guidelines
5. Write/update tests
6. Commit your changes
   ```bash
   git commit -m "Add: brief description of changes"
   ```
7. Push to your fork
   ```bash
   git push origin feature/your-feature-name
   ```
8. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Write tests for new features

### Commit Message Format

```
Type: Brief description

Detailed description (optional)

Types: Add, Update, Fix, Remove, Refactor, Docs
```

### Pull Request Guidelines

- Provide a clear description of changes
- Reference related issues
- Ensure all tests pass
- Update documentation if needed
- Keep PRs focused and atomic

---

## 📚 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [DaisyUI Documentation](https://daisyui.com/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Alpine.js Documentation](https://alpinejs.dev/)
