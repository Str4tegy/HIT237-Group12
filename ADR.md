# Architecture Decision Records

This file records the main architectural decisions for Assessment 2. Each entry includes the problem context, alternatives considered, the final decision, and exact code references.

---

## ADR 001: Split the system into focused Django apps

**Status:** Accepted  
**Date:** 2026-04-14

### Context
The project brief contains three distinct concerns: a fauna database, a submission workflow, and a moderation process. Keeping these concerns in a single app would make the code harder to reason about, harder to test, and more difficult for different group members to work on in parallel.

### Alternatives considered
1. **Single monolithic app**  
   - Pros: fewer files, simpler imports at the beginning  
   - Cons: mixes unrelated responsibilities, increases coupling, harder to allocate team work
2. **Feature-based split into Django apps**  
   - Pros: clearer ownership boundaries, easier URL separation, better reuse, fits Django conventions  
   - Cons: more files and cross-app imports to manage

### Decision
Use separate Django apps for `species`, `submissions`, `accounts`, and `moderation`, with the project URL configuration composing them together.

### Rationale
This choice supports **loose coupling** and makes the architecture easier to explain during the walkthrough. It also aligns with the team role split in the brief: data model work, views/URLs, templates, and documentation can progress with fewer merge conflicts.

### Code reference
- `animals_proj/animals_proj/settings.py:13-24`
- `animals_proj/animals_proj/urls.py:9-17`

### Consequences
- Cross-app imports must be managed carefully.
- The structure is easier to extend later, for example by adding data import commands or API endpoints.
- The resulting codebase is clearer for ADR traceability and viva discussion.

---

## ADR 002: Use a profile model for verification and role-based permissions

**Status:** Accepted  
**Date:** 2026-04-14

### Context
The brief requires different behaviours for guests, citizen scientists, researchers, moderators, and admins. The team needed explicit and auditable role checks for submission creation and moderation review.

### Alternatives considered
1. **Rely only on Django's built-in `is_staff` and `is_superuser` flags**  
   - Pros: very little code  
   - Cons: cannot represent verified researchers or citizen scientists clearly
2. **Create a custom user model**  
   - Pros: centralises role fields in the auth model  
   - Cons: introduces more migration complexity late in the project
3. **Use a separate `Profile` model linked to Django's `User` model**  
   - Pros: simpler than a custom user model, keeps authentication standard, supports explicit roles and verification  
   - Cons: requires profile lookups and profile creation handling

### Decision
Use Django's built-in `User` model with a one-to-one `Profile` model containing `role` and `verified`, and enforce access through reusable permission mixins.

### Rationale
This choice supports **explicit is better than implicit** because the access rules are written directly in model fields and mixins rather than hidden in scattered view logic. It also supports **DRY** because the same permission checks are reused across create, update, delete, and moderation views.

### Code reference
- `animals_proj/animals_proj/accounts/models.py:5-24`
- `animals_proj/animals_proj/permissions.py:8-59`
- `animals_proj/animals_proj/accounts/views.py:14-55`

### Consequences
- Profiles must exist for authenticated users.
- Admin verification becomes a visible part of the workflow.
- The permission model is easier to justify in the live walkthrough.

---

## ADR 003: Model anomaly handling as a separate Flag workflow instead of a boolean on Submission

**Status:** Accepted  
**Date:** 2026-04-14

### Context
The brief requires users to flag suspicious submissions and moderators to review them. A simple boolean such as `is_flagged` on `Submission` would not preserve who reported the issue, why it was reported, or how the moderator resolved it.

### Alternatives considered
1. **Boolean flag on `Submission`**  
   - Pros: minimal schema  
   - Cons: no audit trail, no reason text, no reviewer history
2. **Store moderation notes directly on `Submission`**  
   - Pros: fewer tables  
   - Cons: mixes public submission data with moderation data and supports only one review history record
3. **Separate `Flag` model linked to `Submission`**  
   - Pros: supports multiple reports, moderation decisions, reviewer notes, and traceability  
   - Cons: adds another relationship and extra views/forms

### Decision
Create a dedicated `Flag` model related to `Submission`, then use moderator views to apply review outcomes back to the submission status.

### Rationale
This design better represents the domain and preserves moderation history. It also improves object-oriented decomposition by keeping submission content separate from moderation activity.

### Code reference
- `animals_proj/animals_proj/moderation/models.py:8-54`
- `animals_proj/animals_proj/moderation/views.py:12-97`
- `animals_proj/animals_proj/submissions/models.py:36-78`

### Consequences
- More joins are required when displaying submission moderation history.
- Moderation is easier to explain because each flag has a reporter, reason, decision, and reviewer.
- Future extensions such as multiple flag categories or escalation states are easier to add.

---

## ADR 004: Use class-based views plus QuerySet helpers for list, detail, and CRUD behaviour

**Status:** Accepted  
**Date:** 2026-04-14

### Context
The application needs several repeated patterns: searchable list pages, detail pages, create/update/delete flows, and filtered recent activity. Writing all of these as function-based views would repeat logic for querying, pagination, and template wiring.

### Alternatives considered
1. **Function-based views everywhere**  
   - Pros: direct and flexible  
   - Cons: more repeated boilerplate for CRUD patterns and list handling
2. **Class-based generic views with custom QuerySet methods**  
   - Pros: concise CRUD structure, reusable filtering, easier to keep behaviour consistent  
   - Cons: requires stronger understanding of Django generics

### Decision
Use Django's generic class-based views for the core pages, combined with reusable QuerySet helpers such as `visible_to`, `for_owner`, and `search`.

### Rationale
This choice demonstrates a desirable Django pattern for the assessment. It also supports **DRY** by keeping common query behaviour in one place and improves maintainability as the app grows.

### Code reference
- `animals_proj/animals_proj/submissions/models.py:10-33`
- `animals_proj/animals_proj/submissions/views.py:12-80`
- `animals_proj/animals_proj/species/views.py:8-67`
- `animals_proj/animals_proj/views.py:7-18`

### Consequences
- Developers need to understand Django's generic view lifecycle.
- The project is easier to extend with pagination, filtering, and alternate templates.
- The codebase provides stronger evidence of architectural understanding than a purely scaffolded procedural approach.

---

## ADR 005: Provide live species lookup through a lightweight JSON autocomplete endpoint

**Status:** Accepted  
**Date:** 2026-04-14

### Context
The brief requires fauna search with live results during submission. The project needed a lightweight approach that works with server-rendered Django templates and does not require a full JavaScript framework.

### Alternatives considered
1. **Large static dropdown of all species**  
   - Pros: easy to implement  
   - Cons: poor usability as the species list grows
2. **Separate dedicated search page**  
   - Pros: simple backend  
   - Cons: breaks the submission flow and adds extra clicks
3. **JSON autocomplete endpoint consumed by a small template script**  
   - Pros: responsive UX, minimal JavaScript, works with the existing Django form  
   - Cons: requires one extra endpoint and client-side scripting

### Decision
Expose a small JSON endpoint for species search and connect it to the submission form with lightweight JavaScript.

### Rationale
This keeps the implementation simple while satisfying the live-search requirement. It also keeps the design server-rendered and consistent with the rest of the application.

### Code reference
- `animals_proj/animals_proj/species/views.py:51-67`
- `animals_proj/templates/submissions/form.html:25-56`

### Consequences
- JavaScript is still required for the live interaction.
- The feature remains easy to understand and demo because the backend and frontend behaviour are both small and explicit.
