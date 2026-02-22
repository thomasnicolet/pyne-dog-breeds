-- Fact table for dashboard: life span and weight analytics per breed
with dim as (
    select * from {{ ref('dim_breed') }}
)

select
    breed_id,
    name,
    breed_group,
    size_class,
    life_span_min_years,
    life_span_max_years,
    life_span_avg_years,
    weight_min_lbs,
    weight_max_lbs,
    weight_min_kg,
    weight_max_kg,
    height_min_in,
    height_max_in

from dim
where life_span_avg_years is not null
  and weight_max_lbs is not null
