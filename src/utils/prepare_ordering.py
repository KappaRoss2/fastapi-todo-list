from sqlalchemy import asc, desc


def prepare_ordering(ordering: tuple) -> list:
    """Преобразуем правило сортировки в вид [asc(Поле 1), desc(Поле 2), ...].

    Args:
        ordering (tuple): Правило сортировки.

    Returns:
        list: Преобразованное правило сортировки.
    """
    sort_direction_map = {
        'asc': asc,
        'desc': desc,
    }
    result = []
    for field, sort_direction in ordering:
        sort_direction_func = sort_direction_map.get(sort_direction)
        result.append(sort_direction_func(field))
    return result
