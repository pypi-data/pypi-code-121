def pachyderm_progress_printer(iterable, desc: str = ''):
    try:
        length = len(iterable)
    except TypeError:
        yield from iterable

    N = 30

    bins = list(range(N))

    last_round = -1
    for i, x in enumerate(iterable):
        percent_round = int(round(i / length*100))
        if percent_round % 5 == 0 and percent_round > last_round:
            print(f'{desc}: [{"#"*(bins[int(((i)/length )*N)]+1):<30}] {percent_round:>3d}% ({i:>5}/{length})')
            last_round = percent_round
        yield x
