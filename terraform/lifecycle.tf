# B1 — The Glacier cost gotcha
#
# Sold listings' photos archive to Glacier 30 days after upload, to cut storage cost. Separately
# (not modeled in Terraform — it's an application-level flow), a seller can request deletion of
# their listing data, which must happen within 30 days of the request.
#
# Fix: replaced GLACIER with INTELLIGENT_TIERING. Intelligent-Tiering has no minimum storage
# duration charge, so early deletions (e.g. a seller's right-to-delete at day 40) don't incur
# the hidden 90-day minimum penalty that Glacier carries. Objects accessed infrequently still
# land in cheaper storage tiers automatically, without locking in a minimum retention cost.

resource "aws_s3_bucket" "listing_media" {
  bucket = "haven-listing-media"
}

resource "aws_s3_bucket_intelligent_tiering_configuration" "listing_media_tiering" {
  bucket = aws_s3_bucket.listing_media.id
  name   = "archive-sold-listing-photos"
  status = "Enabled"

  tiering {
    access_tier = "ARCHIVE_ACCESS"
    days        = 90
  }

  tiering {
    access_tier = "DEEP_ARCHIVE_ACCESS"
    days        = 180
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "listing_media_cold" {
  bucket = aws_s3_bucket.listing_media.id

  rule {
    id     = "cold-tier-unaccessed-30d"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "GLACIER_IR"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive" {
  bucket = aws_s3_bucket.listing_media.id

  rule {
    id     = "archive-sold-listing-photos"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "INTELLIGENT_TIERING"
    }
  }
}
