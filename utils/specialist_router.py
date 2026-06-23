VALID_SPECIALISTS = {
    "match",
    "news",
    "community",
    "none"
}

def validate_specialist(
    specialist: str
):
    return (
        specialist
        in VALID_SPECIALISTS
    )