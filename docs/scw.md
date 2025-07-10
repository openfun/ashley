# Media files management with Scaleway

We now use Scaleway S3 to store media files and Scaleway Edge Services to distribute them. Bucket, distribution and IAM users creation is fully automated using [Terraform](https://www.terraform.io/).

Unlike AWS Cloudfront, Scaleway Edge Services does not support proxying static files. However, due to their small size, the impact on bandwidth usage is expected to be minimal.

> ✋ If you plan to develop locally on a site, you don't have to configure
> anything more. The following documentation targets operational users willing
> to setup a Scaleway infrastructure to handle media files.

## Scaleway Credentials

To bootstrap the Scaleway infrastructure, you will first need to edit the
`env.d/terraform` environment file with your Scaleway credentials and settings. You can
start by copying the `env.d/terraform.dist` template _via_ the `make env.d/terraform`
command. Now edit this new file with your Scaleway secrets:

```
# env.d/terraform
#
# SCW admin credentials for creating the s3 state bucket
SCW_ACCESS_KEY=yourScwAccessKeyId
SCW_SECRET_KEY=YourSCWSecretAccessKey

# SCW admin credentials for accessing s3 state backend
AWS_ACCESS_KEY_ID=yourScwAccessKeyId
AWS_SECRET_ACCESS_KEY=YourSCWSecretAccessKey

# Terraform variables
TF_VAR_scw_project_id=yourScwProjectId
TF_VAR_scw_organization_id=yourScwOrganizationId
TF_VAR_scw_user_id=yourScwUserId
TF_VAR_scw_zone=fr-par-1
TF_VAR_scw_region=fr-par

```

> ✋ Note that these credentials should have sufficient access rights to create:
> i. S3 buckets, ii. IAM users and iii. Edge services.

## Setup a shared Terraform state

> ✋ If the project already exists with a shared state, you can skip this
> section and start fetching the state locally to create new workspaces.

If the project doesn't exist at all, you will need to create an S3 bucket to store your Terraform state file by typing the following commands in your terminal:

```
$ bin/state init
$ bin/state apply
```

And voilà! Your shared state is now available to anyone contributing to the
project.

## Create new environments

If everything went smoothly, it's time to initialize your main terraform
project using the shared state:

```
$ bin/terraform init
```

Now that your terraform project is initialized, you will be able to create S3
buckets for media files in various environments (see the [project's
settings](../src/backend/funmooc/settings.py)). To achieve this, we will use
Terraform workspaces with the following paradigm:

_One workspace should be dedicated to one environment_.

You can list existing workspaces _via_:

```
$ bin/terraform workspace list
```

By default, only the `default` workspace exists and is active. You can create
a new one for the `staging` environment _via_:

```
$ bin/terraform workspace new staging
```

Once created and active, we will use this workspace to create `staging` S3
buckets, IAM user and Edge service distribution:

```
$ bin/terraform apply
```

All created objects should be namespaced with the current active workspace
(_e.g._ `staging`). You can check this once logged in to your Scaleway console.

To create the same objects for a different `environment` (_e.g._ `feature`,
`preprod`, or `production`), you should follow the same procedure:

```
$ bin/terraform workspace (new|select) [environment]
$ bin/terraform apply
```

_nota bene_: in the previous pattern, we use the `workspace` `new` or `select`
subcommand depending on the workspace availability.

_Note_: When provisioning the Scaleway Edge Service with Terraform, the `fqdns` attribute (`scaleway_edge_services_dns_stage.media.fqdns`) is not immediately available during the initial `terraform apply`. This results in an "Invalid index" error when trying to output the FQDN. To work around this, you would need to apply a second time.

## Configure runtime environment

Once your buckets have been created for a targeted environment, you will need
to configure your project's runtime environment with the secrets allowing your
Django application to access to those buckets and Edge Services endpoints.
The environment variables use the `AWS` prefix, as required by [django-storages](https://django-storages.readthedocs.io/en/latest/backends/s3_compatible/scaleway.html), even though Scaleway is being used.
The following environment variables should be defined:

- `DJANGO_AWS_S3_CUSTOM_DOMAIN`
- `DJANGO_AWS_ACCESS_KEY_ID`
- `DJANGO_AWS_SECRET_ACCESS_KEY`
- `DJANGO_AWS_STORAGE_BUCKET_NAME`

Corresponding values can be obtained using the following Terraform command:

```
$ bin/terraform output
```

The output should look like the following:

```
edge_service_domain = xxxxxxxxxxxxx.svc.edge.scw.cloud
iam_access_key = XXXXXXXXXXXXXXXXXXXX
iam_access_secret = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Note that the command output is conditioned by the active workspace, beware to
select the expected workspace (_aka_ environment) first (see previous section).
