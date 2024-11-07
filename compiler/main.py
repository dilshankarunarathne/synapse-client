import re

from build import generated_code
from lang.core import main_block, indent
import importlib


def parse_synapse_code(code):
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

    print('parsing complete...')

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


def get_lib_code(im_lib):
    print("reading from library...")
    return im_lib


def parse_data(data):
    # print('------------- data -------------')
    # print(data)
    # print('------------- data -------------')

    return [int(x) for x in data.strip().split('\n')]


def generate_out_code(code, data):
    print("generating code...")

    operations = code['operations']
    imports = code['imports']

    outcode = """# GENERATED CODE BY SYNAPSE LANGUAGE TOOLCHAIN\n\n"""

    # add the actual imports on top
    for im_lib in imports:
        # outcode = outcode + 'import ' + get_lib_code(im_lib) + "\n"
        # TODO: remove hardcoding
        if im_lib == 'lang.lib.math_col':
            math_txt = """def sum_list(input_d):
    return sum(input_d)

    
"""
            outcode = outcode + math_txt
        if im_lib == 'lang.io.r_list':
            # add data block
            data_list = parse_data(data)
            data_block = "\ninput_data = " + str(data_list)
            outcode = outcode + data_block

    outcode = outcode + "\n\n"
    outcode = outcode + main_block

    # do operations
    for operation in operations:
        # remove the starting dot
        operation = operation[1:]
        outcode = outcode + indent + indent + operation

    # print the final code
    # print("-------- outcode ---------")
    # print(outcode)
    # print("-------- outcode ---------")

    # TODO execute the code and return the result
    with open('build/generated_code.py', 'w') as f:
        f.write(outcode)

    return execute_generated_code()


def execute_generated_code():
    # Reload the generated_code module
    importlib.reload(generated_code)

    # Execute the main method and get the result
    result = generated_code.main()
    print("Result from generated code:", result)
    return result


def run_job(code, data):
    try:
        parsed_code = parse_synapse_code(code)
        print("code parsed...")
        return generate_out_code(parsed_code, data)
    except Exception as e:
        print("----Parsing SYN Failed----" + e)
    return None
