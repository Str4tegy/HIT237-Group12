from django.test import TestCase
from django.urls import reverse

from animals_proj.species.models import Species


class SpeciesViewsTests(TestCase):
    def setUp(self):
        self.species = Species.objects.create(
            common_name='Bilby',
            scientific_name='Macrotis lagotis',
            taxon_class='Mammal',
        )

    def test_species_list_renders(self):
        response = self.client.get(reverse('species:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bilby')

    def test_autocomplete_returns_json(self):
        response = self.client.get(reverse('species:autocomplete'), {'q': 'bil'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bilby')
