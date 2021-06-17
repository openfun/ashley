output "media_bucket_name" {
  value = aws_s3_bucket.ashley_media.bucket
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.ashley_cloudfront_distribution.domain_name
}

output "iam_access_key" {
  value = aws_iam_access_key.ashley_access_key.id
  sensitive = true
}

output "iam_access_secret" {
  value = aws_iam_access_key.ashley_access_key.secret
  sensitive = true
}
