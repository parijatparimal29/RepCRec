import argparse
import transaction_manager
import site_manager

def execute_instructions(input_filename):
    tm = transaction_manager.transaction_manager()
    sm = site_manager.site_manager()
    output_str = ""
    with open(input_filename, "r") as read_file:
        output_str += tm.process_instruction(sm, read_file.readline)
    print(output_str)

# get filename from arguments
parser = argparse.ArgumentParser() 
parser.add_argument('--file', help='enter input filename', default='in1.txt')
args = parser.parse_args()
# Use arguments to perform requested action
input_filename = args.file

execute_instructions(input_filename)