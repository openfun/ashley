# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic
Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2022-06-07

### Added

- Show the listing of forums part of the course that would be locked if CTA is
  confirmed

## [1.2.0] - 2022-05-16

### Added

- Enables to lock an entire forum
- Specific endpoints to add and remove group moderator
- Search results directly target the page of the topic of the related post

### Changed

- Stop calculating the list of roles for the endpoint that list users

### Fixed

- search queries to check user's permissions restricted on LTIContext

## [1.1.2] - 2022-01-18

### Added

- use the name of a previous forum with the same `lti_id`
- allow sorting forums on the home page
- add a ribbon icon when an administrator is the writer of a post or a topic

### Fixed

- automatically assign a public_username to instructors and administrators
  when none is defined for a user already existing
- fix pagination for search results

## [1.1.1] - 2021-11-03

### Fixed

- exclude archived forums from the list of forums to move topics to
- exclude archived forums from the list of forums of advanced search


## [1.1.0] - 2021-10-28

### Added

- track forum views, topic and post updates and creations with xAPI events
- allow to search users by any of its meaningful fields in Django admin
- allow to archive a forum with the new `can_archive_forum` permission
- track topic views with XAPI events
- automatically assign a public_username to instructors and administrators
  when none is defined in the LTI authentication
- allow administrators and instructors to move topics to forums in the same
  LTIContext

## [1.0.0] - 2021-08-16

### Fixed

- limit the scope of the unread topics view to the current LTIContext

## [1.0.0-beta.6] - 2021-06-28

### Changed

- Clean built frontend files before each build
- Upgrade node to version 14, the current LTS
- Fix import of the user model in the factory
- Filter search results to current LTIContext

### Added

- add react components to manage moderators for current LTIContext
- add django rest framework to promote/revoke moderators for current LTIContext
- add new role moderator and permission to manage moderators
- allow sorting discussion topics
- add a `LTI ID` field in the sandbox settings to be able to have multiple
  forums for a same LTIContext
- autoload for AshleyEditor component and translation to frontend
- add API endpoint and Amazon S3 to upload image

### Fixed

- fix sorting on sticky and announcements topics

## [1.0.0-beta.5] - 2021-03-01

### Changed

- upgrade django-machina from 1.1.3 to 1.1.4
- add button to insert quotes in the draftjs editor
- limit forum listing to the current user LTIContext id
- add code blocks in the editor and auto-highlight code in the forum
- create a forum for each LTIContext id
- add index to the Forum model

### Fixed

- fix serialization error in search index update
- remove deprecated url in favor of re_path
- prevent inactive users from authenticating via LTI
- prevent linking a User to a LTIContext related to different LTI Consumer

### Added

- add frontend test for draft-js editor
- add a ribbon icon when an instructor is the writer of a post or a topic
- add feature in AshleyEditor to mention any active user in the current topic

## [1.0.0-beta.4] - 2020-12-22

### Added

- enable sentry_sdk in the sandbox
- allow users with empty username to define it

### Changed

- email and public_username are now optional for LTI authentication
- detect and generate unique user id for OpenedX studio users
- get_readable_forums function optimisation

### Fixed

- `upgrades` directory is missing from the published docker image

## [1.0.0-beta.3] - 2020-12-03

### Added

- add permission `can_rename_forum`
- add form to edit the forum name
- add management command `sync_group_permissions`

### Changed

- upgrade django-machina to 1.1.3
- upgrade django-haystack to 3.0
- upgrade django from 3.0 to 3.1
- replace `lti_provider` app with `django-lti-toolbox`
- update translations
- activate search functionality
- update search form template

### Fixed

- fix signature max length errors caused by the draft.js markup
- fix Draft.js editor resize issue with static toolbar

## Removed

- remove `SameSiteNoneMiddleware`

## [1.0.0-beta.2] - 2020-05-18

### Added

- add dependency to bootstrap 4.4.1 and font-awesome 5.13.0
- add button to insert a link in AshleyEditor component

### Changed

- build the forum CSS theme inside ashley instead of using the compiled CSS
  file distributed with django-machina
- coalesce SASS color variables between django-machina and bootstrap
- use a fluid container for a better iframe integration
- change SASS colors

## [1.0.0-beta.1] - 2020-05-04

### Added

- render emoji with emojione on forum posts
- add support for Moodle in ashley's LTI authentication backend
- add SameSiteNoneMiddleware to force SameSite=None on CSRF and session cookies

### Changed

- update draftjs link decorator to open links in new tab and to add attribute
  `rel="nofollow noopener noreferrer"`
- refactor `<AshleyEditor />` in functional component using hooks
- improve focus management on `<AshleyEditor />`

### Fixed

- heading buttons rendering in ashley editor on Firefox

## [1.0.0-beta.0] - 2020-04-16

### Added

- lti_provider django application
- install `django-machina` forum in the `sandbox` project
- custom user model, auth backend and LTI handlers in `ashley`
- standalone LTI consumer to test ashley in development
- permission management and group synchronization based on LTI roles
- `asley.machina_extensions.forum` application to extend django-machina's
  forum model.
- automatic forum creation based on the context of the LTI launch request
- Instructor and Administrator LTI roles have special permissions on their
  forum.
- customize django-machina to have a basic set of forum features
- i18n support and translations with crowdin
- add basic CSS file in ashley to override machina's stylesheet
- each forum has its own unique LTI launch URL
- wysiwyg editor based on Draft.js

### Changed

- Update sandbox settings to be able to run Ashley in an `iframe` on multiple
  external websites

[unreleased]: https://github.com/openfun/ashley/compare/v1.2.1...master
[1.2.1]: https://github.com/openfun/ashley/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/openfun/ashley/compare/v1.1.2...v1.2.0
[1.1.2]: https://github.com/openfun/ashley/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/openfun/ashley/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/openfun/ashley/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/openfun/ashley/compare/v1.0.0-beta.6...v1.0.0
[1.0.0-beta.6]: https://github.com/openfun/ashley/compare/v1.0.0-beta.5...v1.0.0-beta.6
[1.0.0-beta.5]: https://github.com/openfun/ashley/compare/v1.0.0-beta.4...v1.0.0-beta.5
[1.0.0-beta.4]: https://github.com/openfun/ashley/compare/v1.0.0-beta.3...v1.0.0-beta.4
[1.0.0-beta.3]: https://github.com/openfun/ashley/compare/v1.0.0-beta.2...v1.0.0-beta.3
[1.0.0-beta.2]: https://github.com/openfun/ashley/compare/v1.0.0-beta.1...v1.0.0-beta.2
[1.0.0-beta.1]: https://github.com/openfun/ashley/compare/v1.0.0-beta.0...v1.0.0-beta.1
[1.0.0-beta.0]: https://github.com/openfun/ashley/compare/d767ba96aedcbc7d48fba5fefad2b93b9d623cc8...v1.0.0-beta.0
