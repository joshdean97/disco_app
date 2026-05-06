def shift_times_overlap(shift_a, shift_b):
    return (
        shift_a.date == shift_b.date
        and shift_a.start_time < shift_b.end_time
        and shift_a.end_time > shift_b.start_time
    )
