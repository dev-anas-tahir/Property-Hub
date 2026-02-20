# Contributing to Property Hub

Thank you for your interest in contributing to Property Hub! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/Property-Hub.git
   cd Property-Hub
   ```
3. **Set up development environment**
   - Follow the [README.md](../README.md) setup instructions
   - Read the [Architecture Overview](./architecture/overview.md)

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add tests for new features
- Update documentation as needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Run tests (when available)
pytest

# Check code style
ruff check .

# Format code
ruff format .

# Test frontend build
npm run build-css-prod
python manage.py collectstatic --noinput --dry-run
```

### 4. Commit Your Changes

Follow the commit message format:

```
Type: Brief description (50 chars or less)

Detailed description if needed (wrap at 72 chars)

- Bullet points for multiple changes
- Reference issues: Fixes #123
```

**Commit Types:**
- `Add:` - New features or files
- `Update:` - Changes to existing features
- `Fix:` - Bug fixes
- `Remove:` - Removing code or files
- `Refactor:` - Code restructuring
- `Docs:` - Documentation changes
- `Test:` - Test additions or updates
- `Chore:` - Maintenance tasks

**Examples:**
```bash
git commit -m "Add: User profile page with avatar upload"
git commit -m "Fix: Property search not filtering by price range"
git commit -m "Docs: Update deployment checklist with new steps"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots for UI changes
- Test results if applicable

## Code Style Guidelines

### Python

- Follow [PEP 8](https://pep8.org/)
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Maximum line length: 88 characters (Black default)

**Example:**
```python
def calculate_property_price(property: Property, discount: float = 0.0) -> Decimal:
    """
    Calculate the final price of a property with optional discount.

    Args:
        property: The property instance
        discount: Discount percentage (0.0 to 1.0)

    Returns:
        Final price as Decimal
    """
    base_price = property.price
    discount_amount = base_price * Decimal(str(discount))
    return base_price - discount_amount
```

### HTML/Templates

- Use semantic HTML5 elements
- Keep templates DRY (use includes and components)
- Use Tailwind utility classes
- Add ARIA labels for accessibility
- Indent with 2 spaces

**Example:**
```html
{% extends "_layouts/base.html" %}

{% block content %}
<article class="max-w-4xl mx-auto p-6">
  <h1 class="text-3xl font-bold text-gray-900">
    {{ property.title }}
  </h1>

  {% include "_components/properties/property-card.html" %}
</article>
{% endblock %}
```

### CSS

- Prefer Tailwind utilities over custom CSS
- Use `@layer components` for reusable components
- Use `@layer utilities` for custom utilities
- Document complex custom styles

**Example:**
```css
@layer components {
  .property-card {
    @apply bg-white rounded-xl shadow-soft p-6;
    @apply transition-all duration-300;
    @apply hover:shadow-medium hover:-translate-y-1;
  }
}
```

### JavaScript

- Use modern ES6+ syntax
- Prefer Alpine.js for simple interactivity
- Use HTMX for dynamic content
- Add JSDoc comments for functions
- Keep JavaScript minimal

**Example:**
```javascript
/**
 * Initialize property search filters
 * @param {HTMLElement} container - The filter container element
 */
function initPropertyFilters(container) {
  // Implementation
}
```

## Testing Guidelines

### Writing Tests

- Write tests for new features
- Update tests when changing existing features
- Aim for high test coverage
- Test edge cases and error conditions

### Test Structure

```python
from django.test import TestCase
from apps.properties.models import Property

class PropertyModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.property = Property.objects.create(
            title="Test Property",
            price=100000
        )

    def test_property_creation(self):
        """Test that property is created correctly"""
        self.assertEqual(self.property.title, "Test Property")
        self.assertEqual(self.property.price, 100000)

    def test_property_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.property), "Test Property")
```

## Documentation Guidelines

### When to Update Documentation

- Adding new features
- Changing architecture or design patterns
- Updating deployment processes
- Fixing bugs that affect documented behavior

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Keep it up-to-date with code changes
- Follow existing documentation structure

### Where to Add Documentation

- **Architecture changes**: `docs/architecture/`
- **Development guides**: `docs/development/`
- **Deployment updates**: `docs/deployment/`
- **How-to guides**: `docs/guides/`
- **API docs**: Inline docstrings + `docs/api/` (future)

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow format
- [ ] No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Testing
Describe how you tested the changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. Automated checks must pass (linting, tests)
2. At least one approval required
3. Address review comments
4. Squash commits if requested
5. Maintainer will merge when ready

## Getting Help

### Resources

- [Documentation Index](./README.md)
- [Architecture Overview](./architecture/overview.md)
- [Development Guides](./development/)

### Communication

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Features**: Open a GitHub Issue with proposal
- **Security**: Email security@example.com (do not open public issue)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Project documentation (with permission)

## Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search closed issues and PRs
3. Open a GitHub Discussion
4. Ask in project communication channels

Thank you for contributing to Property Hub! 🎉
