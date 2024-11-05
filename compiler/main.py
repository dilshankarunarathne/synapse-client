from lang.io.f_raw import read_file


def translate_code(data: str):
    pass


def _compile(code_input_file_path:str, mode:str, output_file_path:str):
    # read data from file
    data = read_file(code_input_file_path)
    
    return translate_code(data)
    