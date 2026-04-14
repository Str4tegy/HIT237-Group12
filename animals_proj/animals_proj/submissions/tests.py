import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from animals_proj.accounts.models import Profile
from animals_proj.species.models import Species
from animals_proj.submissions.models import Submission


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class SubmissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass12345')
        Profile.objects.create(user=self.user, verified=True, role=Profile.Role.CITIZEN_SCIENTIST)
        self.other_user = User.objects.create_user(username='other', password='pass12345')
        Profile.objects.create(user=self.other_user, verified=True, role=Profile.Role.CITIZEN_SCIENTIST)
        self.species = Species.objects.create(common_name='Northern Quoll', scientific_name='Dasyurus hallucatus')
        self.submission = Submission.objects.create(
            species=self.species,
            submitter=self.user,
            audio=SimpleUploadedFile('sample.mp3', b'audio-bytes', content_type='audio/mpeg'),
            captured_at=timezone.now(),
            confidence=80,
        )

    def test_verified_user_can_open_submission_form(self):
        self.client.login(username='tester', password='pass12345')
        response = self.client.get(reverse('submissions:create'))
        self.assertEqual(response.status_code, 200)

    def test_non_owner_cannot_edit_submission(self):
        self.client.login(username='other', password='pass12345')
        response = self.client.get(reverse('submissions:update', kwargs={'pk': self.submission.pk}))
        self.assertEqual(response.status_code, 403)
