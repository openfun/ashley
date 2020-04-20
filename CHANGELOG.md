# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic 
Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## Added

 - render emoji with emojione on forum posts
 - add support for Moodle in ashley's LTI authentication backend

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

[Unreleased]: https://github.com/openfun/ashley/compare/v1.0.0-beta.0...master
[1.0.0-beta.0]: https://github.com/openfun/ashley/compare/d767ba96aedcbc7d48fba5fefad2b93b9d623cc8...v1.0.0-beta.0
