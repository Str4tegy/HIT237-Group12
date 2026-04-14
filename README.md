# Group12-HIT237

## Project
Listening to NT's Disappearing Animals is a Django web application for browsing NT fauna species, logging acoustic recordings, and moderating anomalous submissions.

## Running the app
The runnable Django project is inside the `animals_proj/` folder.

```bash
cd animals_proj
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install django
python manage.py migrate
python manage.py loaddata animals_proj/species/fixtures/demo_species.json
python manage.py createsuperuser
python manage.py runserver
```

## Main features implemented
- species database with search, filters, detail pages, and copyable coordinates
- audio submission CRUD with owner-or-admin permissions
- profile pages linking submitters to their entries
- recent submission timeline on the home page
- anomaly flagging and moderator review workflow
- live fauna autocomplete endpoint for the submission form
- Django admin configuration for species, submissions, profiles, and flags

## Authentication and roles
- New users can register through the site.
- Admin users verify accounts in Django admin.
- Verified citizen scientists and researchers can create submissions.
- Moderators can review flags through the moderation queue.
- Admin users retain full access through Django admin and owner-or-admin view permissions.

## Project structure
```text
animals_proj/
  manage.py
  animals_proj/
    settings.py
    urls.py
    permissions.py
    views.py
    accounts/
    species/
    submissions/
    moderation/
  templates/
  static/
```

## Testing
```bash
cd animals_proj
python manage.py test
```
