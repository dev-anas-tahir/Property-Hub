# Services / Selectors layer, Forms as I/O only

Business logic lives in `services.py` (writes) and `selectors.py` (reads), per app. Forms become pure I/O adapters: they validate field **shape and format** (regex, type, required) and nothing else. Forms never call `.save()` on a model when a service exists for that entity, and never query the database for business rules. Views are three lines: parse via form, call service/selector, render. Services raise `ApplicationError`; views catch and translate to `form.add_error(None, e.message)` or `messages.error(...)`.

## Why this is surprising

Default Django teaches `ModelForm.save()`, custom managers, and `signals` as the natural homes for write logic. A reader following Django docs will assume `PropertyForm.save()` should persist a Property — it doesn't, by design. The form's `cleaned_data` is passed to `property_create(*, owner, data, images)`, which owns the transaction and validation.

## Consequences

- Every new write-side feature requires touching at least three files (form, service, view) — slower for trivial CRUD, much faster for anything with branching logic.
- Tests can hit services directly without HTTP plumbing.
- Forms are reusable across HTML views and (eventually) management commands or Celery tasks because they hold no transport assumptions.
