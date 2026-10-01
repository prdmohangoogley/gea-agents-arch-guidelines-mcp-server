"""GQL (Graph Query Language) queries for Cloud Spanner Graph."""

# GQL Query: Search guidelines by category or keyword
QUERY_SEARCH_GUIDELINES = """
GRAPH ArchGuidelinesGraph
MATCH (g:Guideline)
WHERE g.category = @category OR g.title LIKE @keyword
RETURN g.guideline_id, g.title, g.category, g.summary, g.source_url
LIMIT @limit;
"""

# GQL Query: Traverse Pattern mitigations
QUERY_PATTERN_MITIGATIONS = """
GRAPH ArchGuidelinesGraph
MATCH (p:Pattern)-[r:MITIGATES]->(a:Antipattern)
WHERE p.name = @pattern_name
RETURN p.name, a.name, a.hazard, a.remedy, r.rationale;
"""

# GQL Query: Get guideline with all implemented patterns
QUERY_GUIDELINE_HIERARCHY = """
GRAPH ArchGuidelinesGraph
MATCH (g:Guideline)-[r:IMPLEMENTS]->(p:Pattern)
WHERE g.guideline_id = @guideline_id
RETURN g.title, p.pattern_id, p.name, p.category, p.description;
"""

# GQL Query: Operational lookup of best practices and patterns by topic
QUERY_BEST_PRACTICES_BY_TOPIC = """
GRAPH ArchGuidelinesGraph
MATCH (g:Guideline)-[r:IMPLEMENTS]->(p:Pattern)
WHERE p.name LIKE @topic OR g.title LIKE @topic OR g.category LIKE @topic
RETURN g.guideline_id, g.title, g.category AS guideline_category, g.summary, p.pattern_id, p.name AS pattern_name, p.category AS pattern_category, p.description AS pattern_description
LIMIT @limit;
"""
