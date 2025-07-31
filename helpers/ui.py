def star_rating_string(stars: float) -> str:
    return "★" * int(stars) + "☆" * (5 - int(stars))