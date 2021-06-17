# A separate terraform project that just creates the bucket where
# we will store the state. It needs to be created before the other
# project because that's where the other project will store its
# state. The state is encrypted using a KMS key because it will
# contain sensitive information.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}
