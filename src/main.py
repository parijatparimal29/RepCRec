import argparse
from os import read
import transaction_manager
import site_manager

def execute_instructions(input_filename):
    tm = transaction_manager.TransactionManager()
    sm = site_manager.SiteManager()
    sm.create_all_sites()
    tick = 0
    with open(input_filename, "r") as read_file:
        for line in read_file:
            tick += 1
            tm.process_instruction(sm, line, tick)

# get filename from arguments
parser = argparse.ArgumentParser() 
parser.add_argument('--file', help='enter input filename', default='in1.txt')
args = parser.parse_args()
# Use arguments to perform requested action
input_filename = args.file

execute_instructions(input_filename)