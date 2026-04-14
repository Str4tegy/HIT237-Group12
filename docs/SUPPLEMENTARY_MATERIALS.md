# Supplementary Materials Guide

This repository now includes the core code and ADRs. For the final submission pack, the team should also include:

## 1. ERD
Suggested entities and relationships:
- `User` 1---1 `Profile`
- `Species` 1---many `Submission`
- `User` 1---many `Submission` as submitter
- `Submission` 1---many `Flag`
- `User` 1---many `Flag` as reporter
- `User` 1---many `Flag` as reviewer

## 2. Class diagram
Suggested classes to show:
- `Profile`
- `Species`
- `Submission`
- `Flag`
- `SubmissionQuerySet`
- `VerifiedSubmitterRequiredMixin`
- `ModeratorRequiredMixin`
- `OwnerOrAdminRequiredMixin`

## 3. Screenshots for evidence
Recommended screenshots to capture:
- home page timeline
- species list and species detail page
- submission create form with autocomplete in use
- submission detail page with audio player and flag button
- moderation queue and moderation review form
- Django admin showing profile verification and species/submission management

## 4. Live walkthrough preparation
Each team member should be ready to explain:
- why the code is separated into apps
- how profile roles and verification work
- how `SubmissionQuerySet` keeps filtering logic DRY
- why `Flag` is a separate model instead of a field on `Submission`
- where the project demonstrates Django philosophies and class-based views
