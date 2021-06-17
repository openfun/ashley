
variable "cloudfront_price_class" {
  type = map(string)

  default = {
    production = "PriceClass_All"
  }
}

variable "app_domain" {
  type = map(string)
}

variable "media_expiration" {
  type = number
  default = 0
}
