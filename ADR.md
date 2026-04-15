# Architecture Decision Records

This file records the main architectural decisions for Assessment 2. Each entry includes the problem context, alternatives considered, the final decision, and exact code references.

---

## ADR 001: Split the system into focused Django apps

**Status:** Accepted  
**Last Edited:** 2026-04-15

### Context
The project plan outlined a website with several features, such as a database of fauna, user submissions, and moderation, etc. Before beginning work, a foundation on which to work on must be made in order for the individual members of the team to develop a cohesive program that respects the sections of the other developers.

### Alternatives considered
1. **A single app**  
   - Pros: fewer files, simpler imports at the beginning  
   - Cons: mixes unrelated responsibilities, harder to allocate team work
2. **Feature-based split into Django apps**  
   - Pros: clearer ownership boundaries, easier URL separation, fits Django conventions  
   - Cons: more files and cross-app imports to manage

### Decision
The webpage will be split into seperate Django apps. Modules will be imported as the features require, the seperate apps and sections to be split amongst the team to develop.

### Rationale
The decision was made as it best reflects the requirements of the app and the skills of the developers. Django is a well documented structure that's modular model would fit the project's specific needs well, whilst also being topic that all the members of the development team have experience in.

### Code reference
- `animals_proj/animals_proj/settings.py:13-24`
- `animals_proj/animals_proj/urls.py:9-17`

### Consequences
- Cross-app imports must be managed carefully.
- The structure is easy to extend/alter later, especcially for changes to the aspects of the individual app.
- The code is clearer for analysis and discussion.

---

## ADR 002: Use a profile model for verification and role-based permissions

**Status:** Accepted  
**Last Edited:** 2026-04-15

### Context
The plan outlines several different actions a user can perform on the website that only certain groups of users should be allowed to do, such as making submissions or moderating them.

### Alternatives considered
1. **Rely only on Django's built-in `is_staff` and `is_superuser` flags**  
   - Pros: easy to implement
   - Cons: cannot differentiate between the several sub-admin/moderator roles
2. **Create a custom user model**  
   - Pros: centralises role fields
   - Cons: higher complexity leads to more difficulty to implement
3. **Use a separate `Profile` model linked to Django's `User` model**  
   - Pros: simpler than a custom user model, keeps authentication standard, supports explicit roles and verification  
   - Cons: requires profile lookups and profile creation handling

### Decision
Users and their permissions will be determined using Django's `User` model in combination with the `Profile` model to assign roles to particular users (such as verifief, scientist, etc.) via reuasable permission tags.

### Rationale
This choice supports **explicit is better than implicit** because the access rules are written directly in model fields and mixins rather than hidden in scattered view logic. It also supports **DRY** because the same permission checks are reused across create, update, delete, and moderation views.
The decision was made as it would be much easier to implement in the long run by assigning reusable permission tags using the inbuilt Django `User` models rather than indivudal role creation. It keeps the program's code concise and centralised, not repeating itself each time it is required.

### Code reference
- `animals_proj/animals_proj/accounts/models.py:5-24`
- `animals_proj/animals_proj/permissions.py:8-59`
- `animals_proj/animals_proj/accounts/views.py:14-55`

### Consequences
- Profiles must exist for verified users.
- User permissions are easier to assign.
- The permissions of any particular role are easy to alter and echo across the progam.

---

## ADR 003: Model anomaly handling as a separate Flag workflow

**Status:** Accepted  
**Last Edited:** 2026-04-15

### Context
A key feature of the program is the flagging feature, users can flag submissions for whatever reason to bring the attention of a moderator.

### Alternatives considered
1. **Boolean flag on `Submission`**  
   - Pros: simple to implement, just a boolean trait such as `is_flagged` on submissions.
   - Cons: would not retain as much info as ideal, such as who reported the submission, why, and any action taken
2. **Store moderation notes directly on `Submission`**  
   - Pros: simpler design
   - Cons: mixes public submission data with moderation data jeopardising the security of potentiall sensitive information
3. **Separate `Flag` model linked to `Submission`**  
   - Pros: supports multiple reports, moderation decisions, reviewer notes, and traceability  
   - Cons: adds another relationship and extra views/forms

### Decision
Use a dedicated `Flag` model that is related to, but not directly connected, `Submission` that would only be visible to moderators, containing all the information related to the flaggin history of the post while remaining seperate to the public information.

### Rationale
This design better reflects the project, favouring retaining information over a slim program, it allows for better moderation decision making and record keeping whilst keeping the moderation content seperate from the submisions.

### Code reference
- `animals_proj/animals_proj/moderation/models.py:8-54`
- `animals_proj/animals_proj/moderation/views.py:12-97`
- `animals_proj/animals_proj/submissions/models.py:36-78`

### Consequences
- More layers of movement to present a moderator with the flagging history of a submission.
- Moderation is easier as important information is recorded for the moderator.
- Future modifications to the flagging system will be easily rippled across the program.

---

## ADR 004: Use class-based views plus QuerySet helpers for list, detail, and CRUD behaviour

**Status:** Accepted  
**Last Edited:** 2026-04-15

### Context
The application needs several repeated patterns: searchable list pages, detail pages, create/update/delete flows, and filtered recent activity. Writing all of these as function-based views would repeat logic for querying, pagination, and template wiring.
An application with several pages, as described in the brief, would require several repeating elements, lists, detail pages, create/update/delete flows. Repeatedly making these features for each page would prove to be innefficient.

### Alternatives considered
1. **Function-based views for each page**  
   - Pros: direct and flexible  
   - Cons: A lot of repetition for CRUD functions and list handling
2. **Class-based generic views with custom QuerySet methods**  
   - Pros: concise CRUD functions, reusable filtering, easier upholding of consistency
   - Cons: requires stronger understanding of Django modelling

### Decision
Use Django's generic class-based views for the core pages, combined with reusable QuerySet helpers such as `visible_to`, `for_owner`, and `search`.
The project will integrate generic class-based views for the core pages whilst reusing QuerySet helpers across the code.

### Rationale
This choice demonstrates a desirable Django pattern for the assessment. It also supports **DRY** by keeping common query behaviour in one place and improves maintainability as the app grows.
This method, whilst requiring putting a bit more thought into development, will better adhere to the Django design philsophy DRY, improves future scalability.

### Code reference
- `animals_proj/animals_proj/submissions/models.py:10-33`
- `animals_proj/animals_proj/submissions/views.py:12-80`
- `animals_proj/animals_proj/species/views.py:8-67`
- `animals_proj/animals_proj/views.py:7-18`

### Consequences
- Developers require deeper understanding of Django.
- Improves the future scalability of the project.
- A consistent UI/page layout across the webpage improves cohesiveness.

---

## ADR 005: Provide live species lookup through a lightweight JSON autocomplete endpoint

**Status:** Accepted  
**Last Edited:** 2026-04-15

### Context
The brief requires fauna search with live results during submission. The project needed a lightweight approach that works with server-rendered Django templates and does not require a full JavaScript framework.
The search function of the project users require to sort through the submissions must update with live results as to improv the user exerience, as the project is quite complex alrady, a lightweight system would be ideal.

### Alternatives considered
1. **Large static dropdown of all species**  
   - Pros: easy to implement  
   - Cons: poor scalability with potentially growing lists of species
2. **Separate dedicated search page**  
   - Pros: simple backend  
   - Cons: breaks the user's flow, sacrificing the user experience through unnecessary interactions
3. **JSON autocomplete endpoint consumed by a small template script**  
   - Pros: responsive UX, minimal JavaScript, works with the existing Django form  
   - Cons: requires one extra endpoint and client-side scripting

### Decision
Integrate a small JSON endpoint for species search that attaches to the submission form with minimal JavaScript.

### Rationale
The code is simple to integrate, doesn't sacrifice the speed of the program, appealing user experience

### Code reference
- `animals_proj/animals_proj/species/views.py:51-67`
- `animals_proj/templates/submissions/form.html:25-56`

### Consequences
- JavaScript is required.
- Feaature is otherwise easy to implement for the improved user experience.
