"""GQL (Graph Query Language) queries for Cloud Spanner Graph."""

# GQL Query: Search guidelines by category or keyword
QUERY_SEARCH_GUIDELINES = """
GRAPH ArchGuidelinesGraph
MATCH (g:Guideline)
WHERE (@category IS NULL OR g.category = @category)
  AND (LOWER(g.title) LIKE LOWER(@keyword) OR LOWER(g.summary) LIKE LOWER(@keyword) OR LOWER(g.guideline_id) LIKE LOWER(@keyword))
RETURN g.guideline_id, g.title, g.category, g.summary, g.source_url
LIMIT @limit;
"""

# GQL Query: Get guideline by ID
QUERY_GET_GUIDELINE_BY_ID = """
GRAPH ArchGuidelinesGraph
MATCH (g:Guideline)
WHERE g.guideline_id = @guideline_id OR LOWER(g.guideline_id) LIKE LOWER(@guideline_id)
RETURN g.guideline_id, g.title, g.category, g.summary, g.source_url, g.version_tag, g.content_sha256
LIMIT 1;
"""

# GQL Query: Traverse Pattern mitigations
QUERY_PATTERN_MITIGATIONS = """
GRAPH ArchGuidelinesGraph
MATCH (p:Pattern)-[r:MITIGATES]->(a:Antipattern)
WHERE LOWER(p.name) LIKE LOWER(@pattern_name) OR LOWER(p.pattern_id) LIKE LOWER(@pattern_name)
RETURN p.name AS pattern_name, a.name AS antipattern_name, a.hazard, a.remedy, r.rationale
LIMIT @limit;
"""

# GQL Query: Get guideline with all implemented patterns
QUERY_GUIDELINE_HIERARCHY = """
GRAPH ArchGuidelinesGraph
MATCH (g:Guideline)-[r:IMPLEMENTS]->(p:Pattern)
WHERE g.guideline_id = @guideline_id
RETURN g.title, p.pattern_id, p.name AS pattern_name, p.category, p.description;
"""

# GQL Query: Operational lookup of best practices and patterns by topic
QUERY_BEST_PRACTICES_BY_TOPIC = """
GRAPH ArchGuidelinesGraph
MATCH (g:Guideline)-[r:IMPLEMENTS]->(p:Pattern)
WHERE LOWER(p.name) LIKE LOWER(@topic) OR LOWER(g.title) LIKE LOWER(@topic) OR LOWER(g.category) LIKE LOWER(@topic)
RETURN g.guideline_id, g.title, g.category AS guideline_category, g.summary, p.pattern_id, p.name AS pattern_name, p.category AS pattern_category, p.description AS pattern_description
LIMIT @limit;
"""

# GQL Query: Retrieve FDE Rubric Items
QUERY_RUBRIC_ITEMS = """
GRAPH ArchGuidelinesGraph
MATCH (f:FDERubricItem)
WHERE (@domain IS NULL OR LOWER(f.domain) LIKE LOWER(@domain))
  AND (@rubric_id IS NULL OR f.rubric_id = @rubric_id)
RETURN f.rubric_id, f.domain, f.sub_competency, f.criteria_level_2, f.criteria_level_3
LIMIT @limit;
"""

# GQL Query: Retrieve Guidelines Enforcing a Specific Rubric Item
QUERY_RUBRIC_ENFORCEMENT = """
GRAPH ArchGuidelinesGraph
MATCH (g:Guideline)-[r:ENFORCES_RUBRIC]->(f:FDERubricItem)
WHERE f.rubric_id = @rubric_id OR LOWER(f.sub_competency) LIKE LOWER(@keyword)
RETURN g.guideline_id, g.title, g.category, r.enforcement_level, r.notes, f.rubric_id, f.sub_competency
ORDER BY g.guideline_id
LIMIT @limit;
"""

# GQL Query: Retrieve Architectural Tradeoffs
QUERY_TRADEOFFS = """
GRAPH ArchGuidelinesGraph
MATCH (t:Tradeoff)
WHERE LOWER(t.option_a) LIKE LOWER(@opt)
   OR LOWER(t.option_b) LIKE LOWER(@opt)
   OR LOWER(t.dimension) LIKE LOWER(@opt)
RETURN t.tradeoff_id, t.dimension, t.option_a, t.option_b, t.analysis
LIMIT @limit;
"""
