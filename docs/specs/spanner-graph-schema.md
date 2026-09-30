# Cloud Spanner Graph Schema Specification

## 1. Overview
Cloud Spanner Graph combines relational and property graph capabilities. This schema defines the tables and the `PROPERTY GRAPH` definition used to store the architectural guidelines knowledge base.

## 2. Table Definitions (DDL)

```sql
-- Nodes: Guidelines
CREATE TABLE Guidelines (
    guideline_id STRING(64) NOT NULL,
    title STRING(256) NOT NULL,
    category STRING(64) NOT NULL,
    summary STRING(MAX),
    source_url STRING(512),
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true)
) PRIMARY KEY (guideline_id);

-- Nodes: Patterns
CREATE TABLE Patterns (
    pattern_id STRING(64) NOT NULL,
    name STRING(128) NOT NULL,
    category STRING(64) NOT NULL,
    description STRING(MAX),
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true)
) PRIMARY KEY (pattern_id);

-- Nodes: Tradeoffs
CREATE TABLE Tradeoffs (
    tradeoff_id STRING(64) NOT NULL,
    dimension STRING(64) NOT NULL,
    option_a STRING(128) NOT NULL,
    option_b STRING(128) NOT NULL,
    analysis STRING(MAX),
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true)
) PRIMARY KEY (tradeoff_id);

-- Nodes: Antipatterns
CREATE TABLE Antipatterns (
    antipattern_id STRING(64) NOT NULL,
    name STRING(128) NOT NULL,
    hazard STRING(MAX) NOT NULL,
    remedy STRING(MAX),
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true)
) PRIMARY KEY (antipattern_id);

-- Edges: PatternMitigatesAntipattern
CREATE TABLE PatternMitigatesAntipattern (
    pattern_id STRING(64) NOT NULL,
    antipattern_id STRING(64) NOT NULL,
    rationale STRING(MAX),
    CONSTRAINT FK_PatternMitigates_Pattern FOREIGN KEY (pattern_id) REFERENCES Patterns (pattern_id),
    CONSTRAINT FK_PatternMitigates_Antipattern FOREIGN KEY (antipattern_id) REFERENCES Antipatterns (antipattern_id)
) PRIMARY KEY (pattern_id, antipattern_id);

-- Edges: GuidelineImplementsPattern
CREATE TABLE GuidelineImplementsPattern (
    guideline_id STRING(64) NOT NULL,
    pattern_id STRING(64) NOT NULL,
    notes STRING(MAX),
    CONSTRAINT FK_GuidelineImplements_Guideline FOREIGN KEY (guideline_id) REFERENCES Guidelines (guideline_id),
    CONSTRAINT FK_GuidelineImplements_Pattern FOREIGN KEY (pattern_id) REFERENCES Patterns (pattern_id)
) PRIMARY KEY (guideline_id, pattern_id);
```

## 3. Property Graph Definition

```sql
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
  );
```
