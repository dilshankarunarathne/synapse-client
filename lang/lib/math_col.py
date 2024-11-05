def sum_list(l):
    """Return the sum of the elements in the list l."""
    return sum(l)


def multiply_list(l):
    """Return the product of the elements in the list l."""
    result = 1
    for x in l:
        result *= x
    return result


def mean_list(l):
    """Return the mean of the elements in the list l."""
    return sum(l) / len(l)
