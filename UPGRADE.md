# Upgrade instructions

For most upgrades, you just need to run the django migrations with
the following command inside your docker container:

```python manage.py migrate```


(Note : in your development environment, you can run ```make migrate```)


Some upgrades need special upgrade instructions.
They will be documented in this file:


### Unreleased

A new permission has been added in this release : `can_archive_forum`.
By default, this permission will only be added to new users with administrator or
instructor roles. If you want to update the group permissions on users already
existing in the database, to reflect what is defined in the setting
`ASHLEY_DEFAULT_FORUM_ROLES_PERMISSIONS`, you can execute the following
management command :

```python manage.py sync_group_permissions --apply```

Note: You can execute the above command without the `--apply` option to do it in
dry mode and see what changes will be applied to your database.

### Ashley 1.0.0-beta.6

A new permission has been added in this release : `can_manage_moderator`.
By default, this permission will only be added to new users with administrator or
instructor roles. If you want to update the group permissions on users already
existing in the database, to reflect what is defined in the setting
`ASHLEY_DEFAULT_FORUM_ROLES_PERMISSIONS`, you can execute the following
management command :

```python manage.py sync_group_permissions --apply```

Note: You can execute the above command without the `--apply` option to do it in
dry mode and see what changes will be applied to your database.


### Ashley 1.0.0-beta.3

To upgrade from any previous version of ashley to version 1.0.0-beta.3, you must execute
the following instructions:

1) Replace the app `lti_provider` with `lti_toolbox` in your `INSTALLED_APPS` setting
2) Execute the script `python upgrades/1.0.0-beta.3.py`
3) Execute `python manage.py migrate`

A new permission has been added in this release : `can_rename_forum`.
By default, this permission will only be added to new users with administrator or
instructor roles. If you want to update the group permissions on users already
existing in the database, to reflect what is defined in the setting
`ASHLEY_DEFAULT_FORUM_ROLES_PERMISSIONS`, you can execute the following
management command :

```python manage.py sync_group_permissions --apply```

Note: You can execute the above command without the `--apply` option to do it in
dry mode and see what changes will be applied to your database.
