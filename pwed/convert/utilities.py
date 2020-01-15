def find_subranges(lst: list) -> (int, int):
    """Takes a range of sequential numbers (possibly with gaps) and splits them
    in sequential sub-ranges defined by the minimum and maximum value.
    
    Copied from https://github.com/stefsmeets/instamatic/blob/master/instamatic/tools.py#L90
    """
    from operator import itemgetter
    from itertools import groupby

    for key, group in groupby(enumerate(lst), lambda i: i[0] - i[1]):
        group = list(map(itemgetter(1), group))
        yield min(group), max(group)