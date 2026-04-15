### Project Plan

---

## Project Brief 

The extremely diverse fauna of the Northen Territory is under the threat of emerging ecological pressures. This project intends to provide data toward the effort of conservation through the medium of a forum-like website that accommodates both civilian recording and more traditional acoustic monitoring to track the movements and appearances of the NT’S endangered species along with encouraging the civilian users to embrace taking further environmental action.
This project is designed to address the NT’s recent convergent of environmental pressures that threaten the local wildlife and, by extension, way of life. This platform will serve as a community driven way to provide essential information not only for the sake of environmental research but also to act as a passive campaign to spread awareness of the environmental pressures to those communities.
The project will take the form of a website where users can upload recordings of species calls that are recorded in the wild. People will be able to upload, browse, and investigate/flag animals calls as they wish and discuss the information. These entries can be cross-referenced and used as evidence in research done by environmental scientists.
The project is intended to be used by both dedicated ecologists using methods such as acoustic monitoring to upload recordings, who may go on to us the data in their research, and civilians passionate in nature and wildlife hoping to help. The project will help foster a sense of community among the civilian users whilst displaying the urgency of the ecological state of the NT to people who may then take further action regarding the environment.

---

## Key Features

- Species database: A database of NT animal species and their known calls, displayed across categorised HTML pages organised by species. Each animal entry includes a button to copy its recorded GPS coordinates, which users can paste into Google Maps for geographic reference.
- Audio recording submissions: Verified users (researchers and citizen scientists) can submit entries containing an audio recording, location, date and time of capture, and a species confidence score indicating how certain the submitter is of the species identification. Clicking on any submission reveals the submitter's profile and links to their other entries.
- Submission Comments: Verified users can comment on existing submissions, whether it be a challenge to the original submissions’ selected species or an opinion/question on the circumstance of the recording.
- Fauna search with live results: During the submission process, users can search for fauna by name and receive live autocomplete results, streamlining species selection.
- Role-based permissions: Users may only edit or delete their own submissions. Admin users have elevated permissions to edit or delete any entry across the platform.
- Recent entries section: The home page displays the most recently submitted recordings, giving visitors an immediate view of current activity.
- Anomaly flagging: Any user can flag a submission they believe to be incorrect or suspicious. for example, a species recorded outside its known habitat. Flagged entries are escalated to a moderator, who reviews the entry and takes appropriate action.  

---

## User and Roles

**Role: Permissions**
Guest:  Browse species database and public entries 
Citizen Scientist / Researcher:  Submit entries, edit/delete own entries, flag anomalies 	
Moderator:  Review flagged entries, take action 
Admin:  Full CRUD over all entries and user data 

---

## Data and External Sources

The app will draw on publicly available NT biodiversity datasets to pre-populate the species database and provide geographic reference data:\

- NT Fauna Atlas: vertebrate fauna records with geographic locations (data.nt.gov.au, CC BY 4.0)
- NT Fauna Species Checklist: full taxa list with conservation status and native/endemic/introduced classification
- Atlas of Living Australia (ALA): national occurrence records with API access
- Threatened Species Index — NT Factsheet: temporal trend data for 395 threatened species
- NT Threatened Animals listing: conservation status per species (nt.gov.au)

---

## Goals

The Northern Territory’s wildlife is threatened by new and growing environmental pressures. The goal of this project to provide crucial information on the movement and conditions of endangered species in the NT to the organisations that need it by providing a way to share and review recordings of species calls recorded in the wild.

---

## Django Design Touchpoints

The application will demonstrate at least three of Django's core design philosophies, which the team should keep in mind throughout development. Current candidates include:

- Don't repeat yourself (DRY): shared logic (e.g. entry validation, permission checks) will be centralised in reusable model methods and mixins rather than duplicated across views
- Loose coupling: the fauna database, submission system, and moderation workflow will be structured as distinct Django apps with clean interfaces between them
- Explicit is better than implicit: user permissions and role-based access will be handled with explicit checks rather than relying on implicit behaviour, making the access model easier to audit and extend

---

## Team Roles and Responsibilities

**Member:  Responsibilities**
Pana:  Data models and database design (ERD, migrations) 
Safiyan:  Views and URL routing (class-based views, QuerySet APIs) 
Kosta:  Templates and front-end (HTML, forms, UI) 
Jorge: ADRs, documentation, and supplementary materials 

---

## Design Inspirations

The design of the website is inspired by common websites such as blogs and public forums with a focus being placed on community input to maximise the productivity of the website. In most author’s websites there is a blog section where the author posts updates about their life, whether it be the progress made on their next novel or something like an opinion piece. These blogs usually have a way of sorting between the different types of posts, i.e. if a user wanted to check the progress of the next book in a series, they would check the ‘writing’ section, or if a user wanted a recommendation, they would check the ‘reviews’ section. Additionally, these blogs tend to have a ‘comment’ feature, so any fans of the author can leave their opinions on any given article to be seen.
The project is essentially an author’s blog combined with the fundamentals of a public forum where anyone can post; however, instead of posting novel updates, users would upload structured entries of wildlife findings including dates, times, locations, and audio recordings in a post, organised by the species they suspect to have recorded. Other users may leave comments with opinions on whether the identified species is correct, or theories on why species may be behaving in a particular way. This idea is being pursued as it not only serves as a platform to harvest information but to build a sense of community between the users to foster a greater communal sense of responsibility for the environment.

---

## Assumptions

Whilst it isn’t necessarily the main aim, the project aims to spread awareness around the pressures that threaten local wildlife to the communities that are closest to them. This project assumes that the people in these communities not only have a way to record the information that they gather but have an interest to record the sounds of nature that they hear and are willing put in the effort of recording and uploading the audio.



