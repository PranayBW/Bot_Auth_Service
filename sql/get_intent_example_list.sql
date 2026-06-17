SELECT
    example_text
FROM intent_training_example
WHERE
    intent_code = $1
    AND is_active = TRUE;