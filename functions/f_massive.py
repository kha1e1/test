def separation_massive(
        data: list,
        records: int
):
    """
    1        2
    [9:00, 9:30, 10:00, 10:30] records 2 (час)

    [9:00,

    """

    b = []
    c = []
    for index, date in enumerate(data, 1):

        c.append(date)
        if index % int(records) == 0:
            b.append(c)
            c = []

    if c:
        b.append(c)

    if records == 1:
        b = b[:-1]  # Не знаю как лучше сделать. Задача выдать рабочее время юзеру

    return b
