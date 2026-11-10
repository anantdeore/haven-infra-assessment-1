variable "landlord_accounts" {
  type        = set(string)
  description = "Landlord account IDs. Order is irrelevant — resources are keyed by account ID, not list position."
  default     = ["la-001", "la-002", "la-003", "la-004"]
}
