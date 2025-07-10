# A separate terraform project that just creates the bucket where
# we will store the state. It needs to be created before the other
# project because that's where the other project will store its
# state.

terraform {
  required_providers {
    scaleway = {
      source  = "scaleway/scaleway"
    }
  }
  required_version = ">= 0.13"

}


provider "scaleway" {
  region     = var.scw_region
  zone       = var.scw_zone
  project_id = var.scw_project_id
}
