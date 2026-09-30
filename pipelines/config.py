"""Configuration for the NL2KG pipeline."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineConfig(BaseSettings):
    """Pipeline configuration settings loaded from environment or defaults."""

    model_config = SettingsConfigDict(env_prefix="PIPELINE_", env_file=".env", extra="ignore")

    gcp_project_id: str = Field(default="local-dev-project", description="GCP Project ID")
    spanner_instance_id: str = Field(default="gea-arch-guidelines-spanner", description="Spanner instance")
    spanner_database_id: str = Field(default="arch_guidelines_graph", description="Spanner database")
    bq_dataset_id: str = Field(default="gea_arch_guidelines_analytics", description="BigQuery dataset")
    gcs_bucket_name: str = Field(default="gea-arch-guidelines-raw-corpus", description="GCS bucket")
    input_docs_dir: str = Field(default="docs/specs", description="Default directory for input markdown documents")
    output_dir: str = Field(default="build/graph", description="Output directory for generated triples")


config = PipelineConfig()
