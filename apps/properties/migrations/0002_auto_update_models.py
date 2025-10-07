"""Auto migration to update Property, PropertyImage and Favorite models.

Generated manually to reflect model changes: field alterations, indexes and constraints.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models
import django.core.validators
import apps.properties.models


def cleanup_duplicate_primary_images(apps, schema_editor):
    """Ensure only one primary image per property by unsetting older duplicates.

    Keep the most-recently uploaded image as primary when multiple are marked.
    """
    PropertyImage = apps.get_model("properties", "PropertyImage")
    # Find property ids that have more than one primary image
    from django.db.models import Count

    dup_props = (
        PropertyImage.objects.values("property_id")
        .filter(is_primary=True)
        .annotate(cnt=Count("id"))
        .filter(cnt__gt=1)
        .values_list("property_id", flat=True)
    )

    for prop_id in dup_props:
        images = (
            PropertyImage.objects.filter(property_id=prop_id, is_primary=True)
            .order_by("-uploaded_at")
        )
        # Keep the first (most recent) as primary, unset the rest
        keep = True
        for img in images:
            if keep:
                keep = False
                continue
            img.is_primary = False
            img.save(update_fields=["is_primary"])


def cleanup_duplicate_favorites(apps, schema_editor):
    """Remove duplicate Favorite rows for the same (user, property).

    Keep the most recent favorited_at entry.
    """
    Favorite = apps.get_model("properties", "Favorite")
    from django.db.models import Count

    dup_pairs = (
        Favorite.objects.values("user_id", "property_id")
        .annotate(cnt=Count("id"))
        .filter(cnt__gt=1)
        .values("user_id", "property_id")
    )

    for pair in dup_pairs:
        qs = Favorite.objects.filter(user_id=pair["user_id"], property_id=pair["property_id"]).order_by("-favorited_at")
        # Keep first, delete others
        to_delete = qs[1:]
        if to_delete:
            ids = [f.id for f in to_delete]
            Favorite.objects.filter(id__in=ids).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("properties", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="property",
            name="phone_number",
            field=models.CharField(max_length=16, validators=[apps.properties.models.phone_validator]),
        ),
        migrations.AlterField(
            model_name="property",
            name="cnic",
            field=models.CharField(max_length=15, validators=[apps.properties.models.cnic_validator]),
        ),
        migrations.AlterField(
            model_name="property",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name="property",
            name="documents",
            field=models.FileField(blank=True, null=True, upload_to=apps.properties.models.documents_upload_path),
        ),
        migrations.AlterField(
            model_name="property",
            name="is_published",
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AddIndex(
            model_name="property",
            index=models.Index(fields=["created_at"], name="properties_property_created_at_idx"),
        ),
        migrations.AddIndex(
            model_name="property",
            index=models.Index(fields=["price"], name="properties_property_price_idx"),
        ),
        migrations.RunPython(cleanup_duplicate_primary_images, reverse_code=migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="propertyimage",
            constraint=models.UniqueConstraint(
                fields=["property"],
                condition=django.db.models.Q(is_primary=True),
                name="one_primary_image_per_property",
            ),
        ),
        migrations.RunPython(cleanup_duplicate_favorites, reverse_code=migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name="favorite",
            options={
                "ordering": ["-favorited_at"],
                "constraints": [
                    models.UniqueConstraint(fields=["user", "property"], name="unique_user_property_favorite")
                ],
            },
        ),
    ]
