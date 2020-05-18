# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic 
Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/openfun/ashley/compare/v1.0.0-beta.1...master
[1.0.0-beta.1]: https://github.com/openfun/ashley/compare/v1.0.0-beta.0...v1.0.0-beta.1
[1.0.0-beta.0]: https://github.com/openfun/ashley/compare/d767ba96aedcbc7d48fba5fefad2b93b9d623cc8...v1.0.0-beta.0
