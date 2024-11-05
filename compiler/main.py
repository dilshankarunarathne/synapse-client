import re
import os
from lang.io.f_raw import read_input_data
from lang.lib.math_col import sum_list


def parse_synapse_code(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    # Extract sections
    meta_section = re.search(r'<<meta>>(.*?)<<endmeta>>', code, re.DOTALL).group(1)
    def_section = re.search(r'<<def>>(.*?)<<enddef>>', code, re.DOTALL).group(1)
    main_section = re.search(r'<<main>>(.*?)<<endmain>>', code, re.DOTALL).group(1)

    # Parse metadata
    n_clients = int(re.search(r'\.n_clients=(\d+)', meta_section).group(1))
    input_meta = re.search(r'<<input>>(.*?)<<endinput>>', meta_section, re.DOTALL).group(1)
    output_meta = re.search(r'<<output>>(.*?)<<endoutput>>', meta_section, re.DOTALL).group(1)

    input_type = re.search(r'\.type=(\w+)', input_meta).group(1)
    input_sep = re.search(r'\.sep=(\\n)', input_meta).group(1)
    input_name = re.search(r'\.name=(\w+)', input_meta).group(1)

    output_type = re.search(r'\.type=(\w+)', output_meta).group(1)
    output_name = re.search(r'\.name=(\w+)', output_meta).group(1)

    # Parse imports
    imports = re.findall(r'\.import (\S+)', def_section)

    # Parse main operations
    main_operations = main_section.strip().split('\n')

    return {
        'n_clients': n_clients,
        'input': {
            'type': input_type,
            'sep': input_sep,
            'name': input_name
        },
        'output': {
            'type': output_type,
            'name': output_name
        },
        'imports': imports,
        'operations': main_operations
    }


def generate_python_code(parsed_code):
    input_name = parsed_code['input']['name']
    output_name = parsed_code['output']['name']
    operations = parsed_code['operations']

    # Generate Python code
    python_code = f"""
import os
from lang.io.f_raw import read_input_data
from lang.lib.math_col import sum_list

def main():
    input_data = read_input_data('{input_name}')
    {operations[0]}
    with open('{output_name}', 'w') as f:
        f.write(str(output_data))

if __name__ == "__main__":
    main()
"""
    return python_code


def compile_synapse_code(synapse_file_path, output_python_file_path):
    parsed_code = parse_synapse_code(synapse_file_path)
    python_code = generate_python_code(parsed_code)

    with open(output_python_file_path, 'w') as file:
        file.write(python_code)


# Example usage
# compile_synapse_code('example_source/add_list.syn', 'compiled_code.py')
