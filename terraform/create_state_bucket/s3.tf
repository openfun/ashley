resource "scaleway_object_bucket" "state_bucket" {
  name   = "ashley-terraform"
  region = var.scw_region
  project_id = var.scw_project_id

  versioning {
    enabled = true
  }

  tags = {
    Name = "terraform"
  }
}

resource "scaleway_object_bucket_acl" "state_bucket_acl" {
  bucket = scaleway_object_bucket.state_bucket.name
  acl    = "private"
}
