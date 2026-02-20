# Frontend Development Setup

This guide covers the frontend development workflow for Property Hub.

## Directory Structure

```
frontend/                # Frontend source files
└── src/
    ├── input.css       # Tailwind CSS source with @import directives
    ├── chat-client.js  # WebSocket chat client
    └── *.test.js       # Test files

static/                 # Production static assets
├── dist/
│   └── output.css      # Compiled Tailwind CSS
├── images/             # Images
└── js/                 # Static JavaScript files

staticfiles/            # Collected static files (auto-generated)
```

## Why Separate Directories?

The `static/` directory should only contain production-ready assets that Django's `collectstatic` can process directly. Source files with build directives (like Tailwind's `@import`) cause issues with Django's `ManifestStaticFilesStorage`.

**Benefits:**
1. Avoid collectstatic errors with unprocessed directives
2. Clear separation between source and compiled assets
3. Explicit and maintainable build process
4. Follow industry best practices

## Development Workflow

### Initial Setup

1. **Install Node.js dependencies**
   ```bash
   npm install
   ```

2. **Build CSS for the first time**
   ```bash
   npm run build-css-prod
   ```

### Daily Development

1. **Start the CSS watcher** (in a separate terminal)
   ```bash
   npm run build-css
   ```
   This watches for changes and rebuilds automatically.

2. **Start Django development server**
   ```bash
   just runserver
   # or
   python manage.py runserver
   ```

3. **Make changes**
   - Edit templates in `templates/`
   - Add Tailwind classes directly in HTML
   - Modify `frontend/src/input.css` for custom CSS
   - CSS rebuilds automatically

### Build Commands

| Command | Description | When to Use |
|---------|-------------|-------------|
| `npm run build-css` | Watch mode, rebuilds on changes | Daily development |
| `npm run build-css-prod` | One-time minified build | Before deployment, testing production build |

## Working with Tailwind CSS

### Adding Styles

**Option 1: Use Tailwind utility classes** (Recommended)
```html
<div class="bg-primary-500 text-white p-4 rounded-xl">
    Content here
</div>
```

**Option 2: Custom CSS in input.css**
```css
/* frontend/src/input.css */
@layer components {
  .my-custom-component {
    @apply bg-primary-500 text-white p-4 rounded-xl;
  }
}
```

### Custom Theme

The project uses a custom color palette defined in `tailwind.config.js`:

- **Primary**: Indigo (#6366f1) - Main brand color
- **Secondary**: Purple (#d946ef) - Accent color
- **Accent**: Orange (#f97316) - Call-to-action
- **Neutral**: Slate - Text and backgrounds

### Tailwind Configuration

Edit `tailwind.config.js` to:
- Add custom colors
- Extend theme
- Configure plugins
- Set content paths

## Working with JavaScript

### Static JavaScript (No Build)

For simple scripts that don't need compilation:

1. Add file to `static/js/`
2. Reference in template:
   ```html
   {% load static %}
   <script src="{% static 'js/my-script.js' %}"></script>
   ```

### Source JavaScript (Needs Build)

For scripts that need compilation/bundling:

1. Add source to `frontend/src/`
2. Add build script to `package.json`
3. Output to `static/dist/`
4. Reference compiled version in template

## Adding New Assets

### Images
```bash
# Add to static/images/
cp my-image.png static/images/

# Use in template
{% load static %}
<img src="{% static 'images/my-image.png' %}" alt="Description">
```

### Fonts
```bash
# Add to static/fonts/
cp my-font.woff2 static/fonts/

# Reference in CSS
@font-face {
  font-family: 'MyFont';
  src: url('/static/fonts/my-font.woff2') format('woff2');
}
```

### Icons
The project uses SVG icons. Add to `static/images/icons/` and use inline or as img src.

## Production Build

Before deploying:

```bash
# 1. Build minified CSS
npm run build-css-prod

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Verify output
ls -la staticfiles/dist/
```

You should see:
- `output.css` - Original compiled CSS
- `output.[hash].css` - Hashed version for cache-busting
- `*.gz` - Compressed versions

## Troubleshooting

### CSS not updating in browser

1. Check if build completed successfully
2. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)
3. Check browser console for 404 errors
4. Verify `static/dist/output.css` was updated

### Build fails

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Try building again
npm run build-css-prod
```

### collectstatic fails

1. Ensure CSS was built first: `npm run build-css-prod`
2. Check `static/dist/output.css` exists
3. Verify no source files in `static/` directory
4. See [Frontend Architecture](../architecture/frontend.md) for details

### Styles not applied

1. Check template loads correct CSS:
   ```html
   {% load static %}
   <link rel="stylesheet" href="{% static 'dist/output.css' %}">
   ```
2. Verify file exists in `static/dist/`
3. Check browser network tab for 404s
4. Clear browser cache

## Best Practices

### CSS
- Prefer Tailwind utilities over custom CSS
- Use `@layer components` for reusable components
- Use `@layer utilities` for custom utilities
- Keep custom CSS minimal

### JavaScript
- Use Alpine.js for simple interactivity
- Use HTMX for dynamic content loading
- Keep JavaScript minimal and progressive
- Test without JavaScript enabled

### Performance
- Use Tailwind's purge/content configuration
- Minimize custom CSS
- Optimize images before adding
- Use SVG for icons when possible

### Organization
- Keep source files in `frontend/`
- Keep production assets in `static/`
- Never edit compiled files directly
- Commit both source and compiled files (or regenerate in CI/CD)

## Related Documentation

- [Frontend Architecture](../architecture/frontend.md) - Detailed architecture explanation
- [Chat Client](./chat-client.md) - WebSocket chat client documentation
- [Deployment Checklist](../deployment/checklist.md) - Production deployment

## Tools and Extensions

### Recommended VS Code Extensions
- Tailwind CSS IntelliSense
- PostCSS Language Support
- ESLint
- Prettier

### Browser Extensions
- Tailwind CSS DevTools
- Vue.js DevTools (for Alpine.js)

## Getting Help

- Check [Frontend Architecture](../architecture/frontend.md) for design decisions
- Review `tailwind.config.js` for theme configuration
- Check browser console for errors
- Ask the team for help
