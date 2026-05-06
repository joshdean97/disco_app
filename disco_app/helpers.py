def shift_times_overlap(shift_a, shift_b):
    return (
        shift_a.date == shift_b.date
        and shift_a.start_time < shift_b.end_time
        and shift_a.end_time > shift_b.start_time
    )


def calculate_reliability(accepted, completed, cancelled):
    total_history = accepted + completed + cancelled

    if total_history == 0:
        return None

    reliability = ((completed - (cancelled * 0.5)) / total_history) * 100

    return max(0, min(100, reliability))
