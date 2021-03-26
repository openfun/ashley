# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic 
Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

 - Clean built frontend files before each build

### Added
 
 - add frontend internationalisation and react components autoload
 - add django rest framework to promote/revoke moderators for current LTIContext
 - add new role moderator and permission to manage moderators

## [1.0.0-beta.5] - 2020-03-01

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

[Unreleased]: https://github.com/openfun/ashley/compare/v1.0.0-beta.5...master
[1.0.0-beta.5]: https://github.com/openfun/ashley/compare/v1.0.0-beta.4...v1.0.0-beta.5
[1.0.0-beta.4]: https://github.com/openfun/ashley/compare/v1.0.0-beta.3...v1.0.0-beta.4
[1.0.0-beta.3]: https://github.com/openfun/ashley/compare/v1.0.0-beta.2...v1.0.0-beta.3
[1.0.0-beta.2]: https://github.com/openfun/ashley/compare/v1.0.0-beta.1...v1.0.0-beta.2
[1.0.0-beta.1]: https://github.com/openfun/ashley/compare/v1.0.0-beta.0...v1.0.0-beta.1
[1.0.0-beta.0]: https://github.com/openfun/ashley/compare/d767ba96aedcbc7d48fba5fefad2b93b9d623cc8...v1.0.0-beta.0
