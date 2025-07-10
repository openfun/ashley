
variable "scw_zone" {
  description = "Scaleway zone in which the state bucket will be created"
  type = string
  default = "fr-par-1"
}

variable "scw_region" {
  description = "Scaleway region in which the state bucket will be created"
  type = string
  default = "fr-par"
}

variable "scw_project_id" {
  description = "Scaleway project ID to associate the state bucket with"
  type = string
}
