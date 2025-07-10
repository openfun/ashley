output "edge_service_domain" {
  value = "${scaleway_edge_services_dns_stage.media.fqdns[0]}"
}

output "iam_access_key" {
  value = "${scaleway_iam_api_key.ashley_api_key.access_key}"
  sensitive = true
}

output "iam_access_secret" {
  value = "${scaleway_iam_api_key.ashley_api_key.secret_key}"
  sensitive = true
}
