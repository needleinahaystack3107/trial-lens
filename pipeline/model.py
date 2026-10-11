"""Gold layer: a star schema. Facts in the middle, dimensions around it,
bridge tables for the many-to-many links."""

SQL = """
CREATE OR REPLACE TABLE dim_sponsor AS
SELECT row_number() OVER (ORDER BY name) AS sponsor_key, name, sponsor_class
FROM (SELECT sponsor_name AS name, any_value(sponsor_class) AS sponsor_class
      FROM silver_trial GROUP BY sponsor_name);

CREATE OR REPLACE TABLE fact_trial AS
SELECT t.nct_id, t.title, t.phase, t.status, t.enrollment, t.start_date, s.sponsor_key
FROM silver_trial t JOIN dim_sponsor s ON s.name = t.sponsor_name;

CREATE OR REPLACE TEMP TABLE trial_condition AS
SELECT DISTINCT nct_id, lower(trim(unnest(conditions))) AS name FROM silver_trial;

CREATE OR REPLACE TABLE dim_condition AS
SELECT row_number() OVER (ORDER BY name) AS condition_key, name
FROM (SELECT DISTINCT name FROM trial_condition);

CREATE OR REPLACE TABLE bridge_trial_condition AS
SELECT t.nct_id, d.condition_key FROM trial_condition t JOIN dim_condition d USING (name);

CREATE OR REPLACE TEMP TABLE trial_intervention AS
SELECT DISTINCT nct_id,
       split_part(x, ': ', 1) AS intervention_type,
       lower(trim(substr(x, strpos(x, ': ') + 2))) AS name
FROM (SELECT nct_id, unnest(interventions) AS x FROM silver_trial);

CREATE OR REPLACE TABLE dim_intervention AS
SELECT row_number() OVER (ORDER BY name, intervention_type) AS intervention_key,
       name, intervention_type
FROM (SELECT DISTINCT name, intervention_type FROM trial_intervention);

CREATE OR REPLACE TABLE bridge_trial_intervention AS
SELECT t.nct_id, d.intervention_key
FROM trial_intervention t JOIN dim_intervention d USING (name, intervention_type);
"""


def run(con):
    con.execute(SQL)
