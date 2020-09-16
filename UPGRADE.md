# Upgrade instructions

For most upgrades, you just need to run the django migrations with
the following command inside your docker container:

```python manage.py migrate```


(Note : in your development environment, you can run ```make migrate```)


Some upgrades need special upgrade instructions.
They will be documented in this file:


### Ashley 1.0.0-beta.3

To upgrade from any previous version of ashley to version 1.0.0-beta.3, you must execute
the following instructions:

1) Replace the app `lti_provider` with `lti_toolbox` in your `INSTALLED_APPS` setting
2) Execute the script `python upgrades/1.0.0-beta.3.py`
3) Execute `python manage.py migrate`
