
# # Define an Edge service plan
resource "scaleway_edge_services_plan" "media" {
  name = "professional"
}

# Define a pipeline for corresponding media bucket
resource "scaleway_edge_services_pipeline" "media" {
  name = "${terraform.workspace}-ashley-media-pipeline"
}

resource "scaleway_edge_services_backend_stage" "media" {
  pipeline_id = scaleway_edge_services_pipeline.media.id

  s3_backend_config {
    bucket_name   = scaleway_object_bucket.ashley_media.name
    bucket_region = var.scw_region
  }
}

resource "scaleway_edge_services_cache_stage" "media" {
  pipeline_id      = scaleway_edge_services_pipeline.media.id
  backend_stage_id = scaleway_edge_services_backend_stage.media.id

  fallback_ttl = 86400
}

resource "scaleway_edge_services_tls_stage" "media" {
  pipeline_id         = scaleway_edge_services_pipeline.media.id
  cache_stage_id      = scaleway_edge_services_cache_stage.media.id
  # No managed_certificate here to let Scaleway generate a default endpoint without enforcing HTTPS
}

resource "scaleway_edge_services_dns_stage" "media" {
  pipeline_id = scaleway_edge_services_pipeline.media.id
  tls_stage_id = scaleway_edge_services_tls_stage.media.id
  # No fqdns here to let Scaleway generate one
}

resource "scaleway_edge_services_head_stage" "media" {
  pipeline_id   = scaleway_edge_services_pipeline.media.id
  head_stage_id = scaleway_edge_services_dns_stage.media.id
}
