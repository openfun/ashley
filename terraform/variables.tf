
variable "media_expiration" {
  type = number
  default = 0
}

variable "scw_project_id" {
  description = "Scaleway project ID to associate the state bucket with"
  type = string
}

variable "scw_organization_id" {
  description = "Scaleway organization ID"
  type = string
}

variable "scw_user_id" {
  description = "Scaleway user ID for maintaining access to the buckets"
  type = string
}

variable "scw_region" {
  description = "Scaleway region in which the state bucket will be created"
  type = string
  default = "fr-par"
}

variable "scw_zone" {
  description = "Scaleway zone in which the state bucket will be created"
  type = string
  default = "fr-par-1"
}

