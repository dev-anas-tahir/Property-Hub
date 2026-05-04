# Split settings into `config/django/` + `config/settings/`

Settings move from the flat `config/settings/{base,development,production}.py` into HackSoft's two-folder layout:

```
config/
├── django/
│   ├── base.py
│   ├── local.py        # was development.py
│   ├── production.py
│   └── test.py         # added when test config first diverges
└── settings/
    ├── storages.py     # django-storages, S3, localstack
    ├── channels.py     # Channels layer + Redis
    ├── axes.py         # django-axes brute-force protection
    ├── unfold.py       # django-unfold admin theme
    └── whitenoise.py   # static file serving
```

`config/django/base.py` does `from config.settings.<integration> import *` for each integration file. New third-party integrations get their own file rather than accreting into `base.py`.

`development.py` is renamed to `local.py` to match HackSoft naming. The `DJANGO_SETTINGS_MODULE` references in `manage.py`, `wsgi.py`, and `asgi.py` are updated accordingly.

## Why this is surprising

A reader expecting flat Django settings will be confused by the two-folder split — particularly because `config/settings/` and `config/django/` sound interchangeable. The split is intentional: **`django/` = Django runtime config keyed by environment**; **`settings/` = third-party integration toggles, environment-agnostic**.

## Consequences

- Adding a new third-party integration is a one-file change with a clear home.
- Disabling an integration during incident response is easier (comment one import in `base.py`).
- Deploy/CI must update `DJANGO_SETTINGS_MODULE` paths in all environments before merge — not reversible without coordinated rollout.
