def get_input_data(data_file_path: str, mode='int_sep_n') -> list:
    if mode == 'int_sep_n':
        return get_int_sep_n(data_file_path)
    else:
        # TODO: Add more modes
        pass


def get_int_sep_n(file_path: str) -> list:
    # read data from file
    data = read_file(data_file_path)

    # convert data to a list of integers
    return list(map(int, data.split('\n')))

    # return the list
    return data


def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()
