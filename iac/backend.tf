terraform {
  backend "gcs" {
    bucket = "arch-best-practices-mcp-server-tfstate"
    prefix = "terraform/state"
  }
}
