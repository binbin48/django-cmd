def chunk_list(start, end, chunk_size):
    """
    Splits a list into smaller chunks of a specified size.
    Yields:
        list: A chunk of the input list.
    """
    for i in range(start, end, chunk_size):
        yield i, i + chunk_size if i + chunk_size <= end else end
