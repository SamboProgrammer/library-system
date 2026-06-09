terraform {
  required_version = ">= 1.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

# Fixed to use explicit absolute Windows path syntax
provider "kubernetes" {
  config_path = "C:/Users/User/.kube/config"
}

resource "kubernetes_namespace" "library" {
  metadata {
    name = "library-system"
  }
}
