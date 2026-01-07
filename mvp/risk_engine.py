def calculate_risk(speed, distance, cattle_count, night=True):
    speed_w = 0.4
    dist_w = 0.3
    count_w = 0.2
    time_w = 0.1

    night_factor = 1.5 if night else 1.0

    risk = (
        speed_w * speed +
        dist_w * (1 / max(distance, 0.01)) +
        count_w * cattle_count +
        time_w * night_factor
    )

    return min(int(risk * 10), 100)


def risk_level(score):
    if score > 60:
        return "HIGH"
    elif score > 30:
        return "MEDIUM"
    return "LOW"
