"""
species/migrations/0001_initial.py

Creates TaxonomicClass and Species tables.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TaxonomicClass",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("common_name", models.CharField(blank=True, max_length=100, help_text="Layperson name for the class, e.g. 'Reptiles'.")),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Taxonomic Class",
                "verbose_name_plural": "Taxonomic Classes",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Species",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scientific_name", models.CharField(
                    max_length=200,
                    unique=True,
                    help_text="Binomial scientific name, e.g. 'Varanus giganteus'.",
                )),
                ("common_name", models.CharField(
                    max_length=200,
                    help_text="Most widely used common name.",
                )),
                ("taxonomic_class", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="species",
                    to="species.taxonomicclass",
                )),
                ("family", models.CharField(blank=True, max_length=100)),
                ("genus", models.CharField(blank=True, max_length=100)),
                ("conservation_status", models.CharField(
                    choices=[
                        ("LC", "Least Concern"),
                        ("NT", "Near Threatened"),
                        ("VU", "Vulnerable"),
                        ("EN", "Endangered"),
                        ("CR", "Critically Endangered"),
                        ("EW", "Extinct in the Wild"),
                        ("EX", "Extinct"),
                        ("DD", "Data Deficient"),
                    ],
                    default="LC",
                    max_length=2,
                )),
                ("origin", models.CharField(
                    choices=[
                        ("native", "Native"),
                        ("endemic", "Endemic to NT"),
                        ("introduced", "Introduced"),
                    ],
                    default="native",
                    max_length=10,
                )),
                ("known_range_description", models.TextField(
                    blank=True,
                    help_text="Plain-text description of the species' known NT range.",
                )),
                ("range_centroid_lat", models.DecimalField(
                    blank=True,
                    decimal_places=6,
                    max_digits=9,
                    null=True,
                )),
                ("range_centroid_lng", models.DecimalField(
                    blank=True,
                    decimal_places=6,
                    max_digits=9,
                    null=True,
                )),
                ("description", models.TextField(
                    blank=True,
                    help_text="General description of the species for the database page.",
                )),
                ("image", models.ImageField(
                    blank=True,
                    null=True,
                    upload_to="species/images/",
                )),
                ("ala_taxon_id", models.CharField(
                    blank=True,
                    max_length=100,
                    help_text="Atlas of Living Australia taxon identifier.",
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Species",
                "verbose_name_plural": "Species",
                "ordering": ["common_name"],
            },
        ),
        migrations.AddIndex(
            model_name="species",
            index=models.Index(fields=["common_name"], name="idx_species_common_name"),
        ),
        migrations.AddIndex(
            model_name="species",
            index=models.Index(fields=["scientific_name"], name="idx_species_scientific_name"),
        ),
    ]
