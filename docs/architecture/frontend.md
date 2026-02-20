# Frontend Architecture

## Overview

This document explains the frontend architecture and build process for Property Hub, specifically addressing the separation of source files from production assets.

## Problem Statement

When using Django's `ManifestStaticFilesStorage` or `CompressedManifestStaticFilesStorage` with Tailwind CSS, the `collectstatic` command fails if source CSS files containing `@import` directives are in the static files directory. This is because Django tries to resolve these imports during the manifest generation process, but the imported files (like `tailwindcss/base`) don't exist as actual files - they're Tailwind directives.

### Error Example
```
ValueError: The file 'src/tailwindcss/base' could not be found with
<whitenoise.storage.CompressedManifestStaticFilesStorage object>
```

## Solution: Source/Production Separation

We implement a clear separation between source files and production assets:

```
frontend/              # Source files (not collected by Django)
├── src/
│   ├── input.css     # Tailwind source with @import directives
│   └── *.js          # Source JavaScript files
└── README.md

static/               # Production assets (collected by Django)
├── dist/
│   └── output.css    # Compiled Tailwind CSS
├── images/
└── js/
```

## Build Process

### Development

```bash
# Watch mode - rebuilds on file changes
npm run build-css
```

This command:
1. Reads `frontend/src/input.css`
2. Processes Tailwind directives
3. Outputs to `static/dist/output.css`
4. Django serves from `static/` automatically

### Production

```bash
# Build minified CSS
npm run build-css-prod

# Collect all static files
python manage.py collectstatic --noinput
```

This process:
1. Compiles and minifies Tailwind CSS
2. Outputs to `static/dist/output.css`
3. `collectstatic` gathers all files from `static/` to `staticfiles/`
4. WhiteNoise serves with compression and cache-busting

### Docker Build

The Dockerfile handles the complete build:

```dockerfile
# Stage 1: Build
COPY frontend/ /app/frontend/
COPY static/ /app/static/
RUN npm run build-css-prod
RUN python manage.py collectstatic --noinput

# Stage 2: Runtime
COPY --from=builder /app/staticfiles /app/staticfiles
# Note: frontend/ is NOT copied to runtime
```

## Configuration

### package.json

```json
{
  "scripts": {
    "build-css": "tailwindcss -i ./frontend/src/input.css -o ./static/dist/output.css --watch",
    "build-css-prod": "tailwindcss -i ./frontend/src/input.css -o ./static/dist/output.css --minify"
  }
}
```

### tailwind.config.js

```javascript
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/*.py',
    './static/js/**/*.js',
    './frontend/**/*.js',  // Scan frontend for Tailwind classes
  ],
  // ...
}
```

### Django Settings

```python
# Static files configuration
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]  # Only static/, not frontend/

# Storage with cache-busting
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

### .gitignore

```gitignore
# Ignore compiled output (regenerated on build)
static/dist/output.css

# Keep source files in version control
!frontend/
```

## Benefits

1. **No collectstatic errors** - Source files with build directives are never processed by Django
2. **Clear separation** - Obvious distinction between source and production files
3. **Efficient Docker builds** - Multi-stage builds exclude source files from runtime
4. **Standard practice** - Follows industry conventions for Django + modern frontend tooling
5. **Cache-busting works** - ManifestStaticFilesStorage can properly hash compiled files

## Alternative Approaches (Not Used)

### Option 1: --ignore flag
```bash
python manage.py collectstatic --noinput --ignore src/input.css
```
**Pros:** Simple, no restructuring needed
**Cons:** Must remember flag in all deployment scripts, easy to forget

### Option 2: Custom StaticFilesConfig
```python
class CustomStaticFilesConfig(StaticFilesConfig):
    ignore_patterns = ['src/input.css', ...]
```
**Pros:** Permanent solution, no command changes
**Cons:** Requires custom app config, less explicit than file structure

### Option 3: Separate directories (CHOSEN)
**Pros:** Most explicit, follows best practices, no special configuration
**Cons:** Requires restructuring existing projects

## Adding New Assets

### CSS/Styles
1. Edit `frontend/src/input.css` or add Tailwind classes to templates
2. Run `npm run build-css-prod`
3. Commit both source and compiled files (or regenerate in CI/CD)

### JavaScript (needs compilation)
1. Add source to `frontend/src/`
2. Add build script to `package.json`
3. Output to `static/dist/`

### JavaScript (no compilation)
1. Add directly to `static/js/`
2. No build step needed

### Images/Fonts
1. Add to `static/images/` or `static/fonts/`
2. No build step needed

## Troubleshooting

### CSS not updating
- Run `npm run build-css-prod` to rebuild
- Clear browser cache
- Check `static/dist/output.css` was updated

### collectstatic fails
- Ensure `frontend/` is NOT in `STATICFILES_DIRS`
- Verify `static/dist/output.css` exists before running collectstatic
- Check for other source files accidentally in `static/`

### Docker build fails
- Ensure `frontend/` is NOT in `.dockerignore`
- Verify Node.js is installed in builder stage
- Check npm build runs before collectstatic

## References

- [Django Static Files Documentation](https://docs.djangoproject.com/en/stable/howto/static-files/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)
- [Tailwind CSS with Django](https://tailwindcss.com/docs/installation)
- [Production-ready cache-busting for Django and Tailwind CSS](https://www.loopwerk.io/articles/2025/django-tailwind-production/)
