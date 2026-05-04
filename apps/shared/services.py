from django.db import models


def model_update(
    *, instance: models.Model, fields: list[str], data: dict
) -> models.Model:
    for field in fields:
        setattr(instance, field, data[field])
    instance.full_clean()
    instance.save(update_fields=fields)
    return instance
