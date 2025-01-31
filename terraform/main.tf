terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.15.0"
    }
  }
}

provider "google" {
  project = "taxi-data-447320"
  region  = "europe-west2"
}

resource "google_storage_bucket" "bucket-demo" {
  name          = "taxi-data-447320-bucket"
  location      = "EU"
  force_destroy = true

 

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = "zoomcamp"
  project    = "taxi-data-447320"
  location   = "EU"
}