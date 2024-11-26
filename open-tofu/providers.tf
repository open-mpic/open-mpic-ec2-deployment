terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}



# Init a default aws provider for the api deployment.
provider "aws" {
  region                  = "us-east-2"
  profile                 = "default"
}

provider "aws" {
  alias = "us-east-2"
  region = "us-east-2"
}


provider "aws" {
  alias = "us-west-2"
  region = "us-west-2"
}


provider "aws" {
  alias = "eu-central-1"
  region = "eu-central-1"
}
