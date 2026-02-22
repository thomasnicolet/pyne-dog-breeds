with source as (
    select * from {{ source('bronze', 'dog_api_raw') }}
),

cleaned as (
    select
        id                                                              as breed_id,
        name,
        breed_group,
        origin,
        temperament,
        life_span,

        -- parse "10 - 12 years" → min / max
        safe_cast(regexp_extract(life_span, r'^(\d+)')         as int64) as life_span_min_years,
        safe_cast(regexp_extract(life_span, r'- (\d+)')        as int64) as life_span_max_years,

        -- parse "6 - 13" weight strings
        safe_cast(trim(split(weight__imperial, '-')[safe_offset(0)]) as float64) as weight_min_lbs,
        safe_cast(trim(split(weight__imperial, '-')[safe_offset(1)]) as float64) as weight_max_lbs,
        safe_cast(trim(split(weight__metric,   '-')[safe_offset(0)]) as float64) as weight_min_kg,
        safe_cast(trim(split(weight__metric,   '-')[safe_offset(1)]) as float64) as weight_max_kg,

        -- parse "9 - 11.5" height strings
        safe_cast(trim(split(height__imperial, '-')[safe_offset(0)]) as float64) as height_min_in,
        safe_cast(trim(split(height__imperial, '-')[safe_offset(1)]) as float64) as height_max_in,

        reference_image_id

    from source
    where id is not null
)

select * from cleaned
