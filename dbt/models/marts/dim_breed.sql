with stg as (
    select * from {{ ref('stg_breeds') }}
)

select
    breed_id,
    name,
    breed_group,
    origin,
    temperament,
    life_span,
    life_span_min_years,
    life_span_max_years,
    round((coalesce(life_span_min_years, 0) + coalesce(life_span_max_years, life_span_min_years, 0)) / 2.0, 1) as life_span_avg_years,

    weight_min_lbs,
    weight_max_lbs,
    weight_min_kg,
    weight_max_kg,
    height_min_in,
    height_max_in,

    case
        when weight_max_lbs <= 20  then 'Small'
        when weight_max_lbs <= 60  then 'Medium'
        when weight_max_lbs > 60   then 'Large'
        else 'Unknown'
    end as size_class,

    reference_image_id

from stg
