import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from animals_proj.accounts.models import Profile
from animals_proj.moderation.models import Flag
from animals_proj.species.models import Species
from animals_proj.submissions.models import Submission


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class ModerationTests(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(username='mod', password='pass12345')
        Profile.objects.create(user=self.moderator, verified=True, role=Profile.Role.MODERATOR)
        self.reporter = User.objects.create_user(username='reporter', password='pass12345')
        Profile.objects.create(user=self.reporter, verified=True, role=Profile.Role.CITIZEN_SCIENTIST)
        self.species = Species.objects.create(common_name='Gouldian Finch', scientific_name='Erythrura gouldiae')
        self.submission = Submission.objects.create(
            species=self.species,
            submitter=self.reporter,
            audio=SimpleUploadedFile('sample.mp3', b'audio-bytes', content_type='audio/mpeg'),
            captured_at=timezone.now(),
            confidence=70,
        )
        self.flag = Flag.objects.create(submission=self.submission, reporter=self.reporter, reason='Outside known habitat')

    def test_moderator_can_access_queue(self):
        self.client.login(username='mod', password='pass12345')
        response = self.client.get(reverse('moderation:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Outside known habitat')
