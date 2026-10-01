resource "google_spanner_instance" "instance" {
  name             = var.instance_id
  config           = var.config
  display_name     = var.display_name
  processing_units = var.processing_units
  edition          = var.edition
  project          = var.project_id
}

resource "google_spanner_database" "database" {
  instance = google_spanner_instance.instance.name
  name     = var.database_name
  project  = var.project_id

  ddl = [
    <<-EOT
    CREATE TABLE Guidelines (
      guideline_id STRING(64) NOT NULL,
      title STRING(256) NOT NULL,
      category STRING(64) NOT NULL,
      summary STRING(MAX),
      source_url STRING(512),
      created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true)
    ) PRIMARY KEY (guideline_id)
    EOT
    ,
    <<-EOT
    CREATE TABLE Patterns (
      pattern_id STRING(64) NOT NULL,
      name STRING(128) NOT NULL,
      category STRING(64) NOT NULL,
      description STRING(MAX),
      created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true)
    ) PRIMARY KEY (pattern_id)
    EOT
    ,
    <<-EOT
    CREATE TABLE Tradeoffs (
      tradeoff_id STRING(64) NOT NULL,
      dimension STRING(64) NOT NULL,
      option_a STRING(128) NOT NULL,
      option_b STRING(128) NOT NULL,
      analysis STRING(MAX),
      created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true)
    ) PRIMARY KEY (tradeoff_id)
    EOT
    ,
    <<-EOT
    CREATE TABLE Antipatterns (
      antipattern_id STRING(64) NOT NULL,
      name STRING(128) NOT NULL,
      hazard STRING(MAX) NOT NULL,
      remedy STRING(MAX),
      created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true)
    ) PRIMARY KEY (antipattern_id)
    EOT
    ,
    <<-EOT
    CREATE TABLE PatternMitigatesAntipattern (
      pattern_id STRING(64) NOT NULL,
      antipattern_id STRING(64) NOT NULL,
      rationale STRING(MAX),
      CONSTRAINT FK_PatternMitigates_Pattern FOREIGN KEY (pattern_id) REFERENCES Patterns (pattern_id),
      CONSTRAINT FK_PatternMitigates_Antipattern FOREIGN KEY (antipattern_id) REFERENCES Antipatterns (antipattern_id)
    ) PRIMARY KEY (pattern_id, antipattern_id)
    EOT
    ,
    <<-EOT
    CREATE TABLE GuidelineImplementsPattern (
      guideline_id STRING(64) NOT NULL,
      pattern_id STRING(64) NOT NULL,
      notes STRING(MAX),
      CONSTRAINT FK_GuidelineImplements_Guideline FOREIGN KEY (guideline_id) REFERENCES Guidelines (guideline_id),
      CONSTRAINT FK_GuidelineImplements_Pattern FOREIGN KEY (pattern_id) REFERENCES Patterns (pattern_id)
    ) PRIMARY KEY (guideline_id, pattern_id)
    EOT
    ,
    <<-EOT
    CREATE OR REPLACE PROPERTY GRAPH ArchGuidelinesGraph
      NODE TABLES (
        Guidelines
          LABEL Guideline
          PROPERTIES (guideline_id, title, category, summary, source_url),
        Patterns
          LABEL Pattern
          PROPERTIES (pattern_id, name, category, description),
        Tradeoffs
          LABEL Tradeoff
          PROPERTIES (tradeoff_id, dimension, option_a, option_b, analysis),
        Antipatterns
          LABEL Antipattern
          PROPERTIES (antipattern_id, name, hazard, remedy)
      )
      EDGE TABLES (
        PatternMitigatesAntipattern
          SOURCE KEY (pattern_id) REFERENCES Patterns (pattern_id)
          DESTINATION KEY (antipattern_id) REFERENCES Antipatterns (antipattern_id)
          LABEL MITIGATES
          PROPERTIES (rationale),
        GuidelineImplementsPattern
          SOURCE KEY (guideline_id) REFERENCES Guidelines (guideline_id)
          DESTINATION KEY (pattern_id) REFERENCES Patterns (pattern_id)
          LABEL IMPLEMENTS
          PROPERTIES (notes)
      )
    EOT
  ]

  deletion_protection = false
}
