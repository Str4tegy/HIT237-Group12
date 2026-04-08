"""
species/models.py

Data models for the NT fauna species database.

Pana's responsibility:
  - Species taxonomy and classification
  - Conservation status tracking
  - Known call metadata (separate from user-submitted recordings)
  - Geographic range data

Django philosophy demonstrated:
  - DRY: Shared validation logic lives in model clean() methods
  - Loose coupling: Species app has no imports from submissions or moderation
    apps — the dependency arrow only points inward (submissions → species)
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class TaxonomicClass(models.Model):
    """
    Broad vertebrate class grouping (e.g. Reptilia, Mammalia, Aves).

    Used to organise the species browse pages into categories.
    Pre-populated from the NT Fauna Species Checklist dataset.
    """

    name = models.CharField(max_length=100, unique=True)
    common_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Layperson name for the class, e.g. 'Reptiles'.",
    )
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Taxonomic Class"
        verbose_name_plural = "Taxonomic Classes"
        ordering = ["name"]


class Species(models.Model):
    """
    A single NT fauna species with taxonomy, conservation status,
    and geographic context.

    Pre-populated from:
      - NT Fauna Species Checklist (taxa, status, classification)
      - NT Fauna Atlas (geographic reference points)
      - NT Threatened Animals listing (conservation status)

    Relationships:
      - TaxonomicClass (ForeignKey): many species → one class
      - AudioSubmission (reverse FK): one species ← many submissions
    """

    # ------------------------------------------------------------------ #
    # Conservation status choices — sourced from NT Threatened Animals    #
    # listing and EPBC Act categories                                     #
    # ------------------------------------------------------------------ #
    LEAST_CONCERN = "LC"
    NEAR_THREATENED = "NT"
    VULNERABLE = "VU"
    ENDANGERED = "EN"
    CRITICALLY_ENDANGERED = "CR"
    EXTINCT_IN_WILD = "EW"
    EXTINCT = "EX"
    DATA_DEFICIENT = "DD"

    CONSERVATION_STATUS_CHOICES = [
        (LEAST_CONCERN, "Least Concern"),
        (NEAR_THREATENED, "Near Threatened"),
        (VULNERABLE, "Vulnerable"),
        (ENDANGERED, "Endangered"),
        (CRITICALLY_ENDANGERED, "Critically Endangered"),
        (EXTINCT_IN_WILD, "Extinct in the Wild"),
        (EXTINCT, "Extinct"),
        (DATA_DEFICIENT, "Data Deficient"),
    ]

    # ------------------------------------------------------------------ #
    # Origin classification                                               #
    # ------------------------------------------------------------------ #
    NATIVE = "native"
    ENDEMIC = "endemic"
    INTRODUCED = "introduced"

    ORIGIN_CHOICES = [
        (NATIVE, "Native"),
        (ENDEMIC, "Endemic to NT"),
        (INTRODUCED, "Introduced"),
    ]

    # ------------------------------------------------------------------ #
    # Core taxonomy fields                                                #
    # ------------------------------------------------------------------ #
    scientific_name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Binomial scientific name, e.g. 'Varanus giganteus'.",
    )
    common_name = models.CharField(
        max_length=200,
        help_text="Most widely used common name.",
    )
    taxonomic_class = models.ForeignKey(
        TaxonomicClass,
        on_delete=models.PROTECT,   # Prevent orphaning species records
        related_name="species",
    )
    family = models.CharField(max_length=100, blank=True)
    genus = models.CharField(max_length=100, blank=True)

    # ------------------------------------------------------------------ #
    # Classification                                                      #
    # ------------------------------------------------------------------ #
    conservation_status = models.CharField(
        max_length=2,
        choices=CONSERVATION_STATUS_CHOICES,
        default=LEAST_CONCERN,
    )
    origin = models.CharField(
        max_length=10,
        choices=ORIGIN_CHOICES,
        default=NATIVE,
    )

    # ------------------------------------------------------------------ #
    # Geographic reference — used to flag out-of-range submissions       #
    # Stored as decimal degrees (WGS84)                                  #
    # ------------------------------------------------------------------ #
    known_range_description = models.TextField(
        blank=True,
        help_text="Plain-text description of the species' known NT range.",
    )
    # Approximate centroid of known range for map reference
    range_centroid_lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    range_centroid_lng = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------ #
    # General info                                                        #
    # ------------------------------------------------------------------ #
    description = models.TextField(
        blank=True,
        help_text="General description of the species for the database page.",
    )
    image = models.ImageField(
        upload_to="species/images/",
        null=True,
        blank=True,
    )

    # ALA identifier for API cross-referencing
    ala_taxon_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Atlas of Living Australia taxon identifier.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------ #
    # Model methods                                                       #
    # ------------------------------------------------------------------ #

    def get_absolute_url(self) -> str:
        return reverse("species:detail", kwargs={"pk": self.pk})

    @property
    def coordinates_display(self) -> str:
        """
        Returns a copyable coordinate string for the 'Copy GPS' button.
        Out of scope: direct Google Maps integration. Users copy-paste this.
        """
        if self.range_centroid_lat and self.range_centroid_lng:
            return f"{self.range_centroid_lat}, {self.range_centroid_lng}"
        return ""

    @property
    def is_threatened(self) -> bool:
        """True if the species has a nationally significant threat status."""
        return self.conservation_status in (
            self.VULNERABLE,
            self.ENDANGERED,
            self.CRITICALLY_ENDANGERED,
            self.EXTINCT_IN_WILD,
            self.EXTINCT,
        )

    def __str__(self) -> str:
        return f"{self.common_name} ({self.scientific_name})"

    class Meta:
        verbose_name = "Species"
        verbose_name_plural = "Species"
        ordering = ["common_name"]
        indexes = [
            # Speed up the live autocomplete search during entry submission
            models.Index(fields=["common_name"], name="idx_species_common_name"),
            models.Index(fields=["scientific_name"], name="idx_species_scientific_name"),
        ]
