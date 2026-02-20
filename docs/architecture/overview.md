# Architecture Overview

## System Architecture

Property Hub is a modern Django-based real estate management platform with a component-based architecture.

## Technology Stack

### Backend
- **Django 6.0.2** - Web framework
- **Python 3.13+** - Programming language
- **PostgreSQL 17** - Primary database
- **Redis** - Caching and WebSocket channel layer
- **Channels** - WebSocket support for real-time features
- **UV** - Fast Python package manager

### Frontend
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **DaisyUI 4.6** - Component library built on Tailwind
- **HTMX** - Dynamic HTML interactions without JavaScript
- **Alpine.js** - Lightweight JavaScript framework
- **WhiteNoise** - Static file serving with compression

### Infrastructure
- **Docker** - Containerization
- **AWS S3** - Media file storage
- **Localstack** - Local AWS simulation for development

## Application Structure

### Django Apps

```
apps/
├── properties/     # Property listings and management
├── users/          # User authentication and profiles
├── chat/           # Real-time chat functionality
└── shared/         # Shared utilities and base classes
```

Each app follows Django's standard structure:
- `models.py` - Database models
- `views.py` - View logic
- `forms.py` - Form definitions
- `urls.py` - URL routing
- `admin.py` - Admin interface configuration

### Configuration

```
config/
├── settings/
│   ├── base.py         # Base settings for all environments
│   ├── development.py  # Development-specific settings
│   └── production.py   # Production-specific settings
├── urls.py             # Root URL configuration
├── wsgi.py             # WSGI application
├── asgi.py             # ASGI application (for WebSockets)
└── routing.py          # WebSocket routing
```

### Templates

```
templates/
├── _layouts/       # Base layouts (base.html, etc.)
├── _components/    # Reusable UI components
├── properties/     # Property-specific templates
├── users/          # User-specific templates
└── chat/           # Chat-specific templates
```

**Component-Based Approach:**
- Reusable components in `_components/`
- DRY principle for forms, navigation, UI elements
- Separation of layouts, components, and pages

### Static Files

See [Frontend Architecture](./frontend.md) for detailed information.

```
frontend/           # Source files (CSS, JS)
static/             # Production assets
staticfiles/        # Collected files (auto-generated)
```

## Design Patterns

### App-Based Organization
- Domain-driven design with separate apps
- Clear separation of concerns
- Each app is self-contained and reusable
- Shared utilities in `apps/shared/`

### Component-Based Templates
- Reusable UI components
- Consistent design system
- Easy to maintain and update
- DRY principle

### Settings Organization
- Base settings for all environments
- Environment-specific overrides
- Secrets managed via environment variables
- 12-factor app methodology

## Data Flow

### Request/Response Cycle

```
Browser → Django URL Router → View → Template → Response
                                ↓
                            Database
```

### WebSocket Flow (Chat)

```
Browser ← WebSocket → Channels → Redis → Channels → WebSocket → Browser
                         ↓
                     Database
```

## Security

### Authentication
- Custom User model extending AbstractUser
- Django's built-in authentication system
- Django Axes for brute-force protection
- Session-based authentication

### Authorization
- Django's permission system
- Model-level permissions
- View-level decorators
- Template-level checks

### Security Features
- CSRF protection enabled
- XSS protection via template escaping
- SQL injection prevention via ORM
- Secure password hashing (PBKDF2)
- HTTPS enforcement in production
- Security middleware enabled

## Performance

### Caching Strategy
- Redis for session storage
- Template fragment caching
- Database query optimization
- Static file compression (WhiteNoise)

### Database Optimization
- Indexed fields for common queries
- Select/prefetch related for N+1 prevention
- Database connection pooling
- Query optimization

### Static Files
- WhiteNoise for efficient serving
- Gzip compression
- Cache-busting via hashed filenames
- CDN-ready architecture

## Scalability

### Horizontal Scaling
- Stateless application design
- Session storage in Redis
- Media files in S3
- Database connection pooling

### Vertical Scaling
- Efficient database queries
- Caching strategy
- Async task processing (future)
- WebSocket connection management

## Development Workflow

### Local Development
1. Docker Compose for services (PostgreSQL, Redis, Localstack)
2. Django development server
3. Tailwind CSS watch mode
4. Hot reload for templates

### Testing
- Unit tests for models and views
- Integration tests for workflows
- Frontend tests for JavaScript
- E2E tests (future)

### Deployment
- Docker multi-stage builds
- Environment-based configuration
- Automated static file collection
- Health checks

## Future Enhancements

### Planned Features
- Celery for async task processing
- Full-text search (PostgreSQL or Elasticsearch)
- API endpoints (Django REST Framework)
- Mobile app support
- Advanced analytics

### Technical Improvements
- Comprehensive test coverage
- CI/CD pipeline
- Monitoring and logging
- Performance optimization
- API documentation

## Related Documentation

- [Frontend Architecture](./frontend.md) - Frontend structure and build process
- [Backend Architecture](./backend.md) - Detailed backend architecture *(Coming Soon)*
- [Database Schema](./database.md) - Database models and relationships *(Coming Soon)*
- [Deployment Checklist](../deployment/checklist.md) - Production deployment guide
