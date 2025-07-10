# Create S3 Bucket for media files
resource "scaleway_object_bucket" "ashley_media" {
  name = "${terraform.workspace}-ashley-media"
  region = var.scw_region

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
    max_age_seconds = 3600
  }

  versioning {
    enabled = var.media_expiration > 0 ? false : true
  }

  dynamic "lifecycle_rule" {
    for_each = var.media_expiration > 0 ? [1] : []
    content {
      id      = "expiration"
      enabled = true
      expiration {
        days = var.media_expiration
      }
    }
  }

  tags = {
    Name        = "ashley-media"
    Environment = "${terraform.workspace}"
  }
}

# Defines bucket corresponding ACL
resource "scaleway_object_bucket_acl" "ashley_media_acl" {
  bucket = scaleway_object_bucket.ashley_media.name
  acl    = "private"
}

# Defines an application that should have access to the S3 bucket
resource "scaleway_iam_application" "ashley_application" {
  name = "${terraform.workspace}-ashley"
  description = "Ashley application for the media bucket"
}

# Defines a policy so that the application have full access to Object Storage
resource "scaleway_iam_policy" "application_object_full_access" {
  name           = "${terraform.workspace}-ashley-media"
  description    = "Full access to object storage for application"
  application_id = scaleway_iam_application.ashley_application.id

  rule {
    project_ids          = [var.scw_project_id]
    permission_set_names = ["ObjectStorageFullAccess"]
  }
}

# Defines an API key for the application
resource "scaleway_iam_api_key" "ashley_api_key" {
  application_id = scaleway_iam_application.ashley_application.id
  default_project_id = var.scw_project_id
}


# Grant access to the media bucket:
# - read access for all users
# - full access for the application
resource "scaleway_object_bucket_policy" "ashley_media_bucket_policy" {
  bucket = scaleway_object_bucket.ashley_media.id

  policy = jsonencode(
    {
      Version = "2023-04-17",
      Statement = [
        {
          Sid    = "Give GetObject to all users",
          Effect = "Allow",
          Principal = "*",
          Action = [
            "s3:GetObject"
          ]
          Resource = [
            "${scaleway_object_bucket.ashley_media.name}",
            "${scaleway_object_bucket.ashley_media.name}/*"
          ]
        },
        {
          Sid    = "Application access",
          Effect = "Allow",
          Principal = {
            SCW = "application_id:${scaleway_iam_application.ashley_application.id}"
          },
          Action = [
            "*"
          ]
          Resource = [
            "${scaleway_object_bucket.ashley_media.name}",
            "${scaleway_object_bucket.ashley_media.name}/*"
          ]
        },
        {
          Sid    = "Secure statement to maintain access",
          Effect = "Allow",
          Principal = {
            SCW = "user_id:${var.scw_user_id}"
          },
          Action = [
            "*"
          ]
          Resource = [
            "${scaleway_object_bucket.ashley_media.name}",
            "${scaleway_object_bucket.ashley_media.name}/*"
          ]
        }
      ]
    }
  )
}
