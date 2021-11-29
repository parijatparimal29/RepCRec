import argparse
from os import read
import transaction_manager
import site_manager
import os

def execute_instructions(input_filename):
    tm = transaction_manager.TransactionManager()
    sm = site_manager.SiteManager()
    sm.create_all_sites()
    tick = 0
    with open(input_filename, "r") as read_file:
        for line in read_file:
            tick += 1
            tm.process_instruction(sm, line, tick)

def readFolder(path):
    filesList = os.listdir(path)
    for filename in filesList:
        execute_instructions(path+"/"+filename)


# get filename from arguments
parser = argparse.ArgumentParser() 
parser.add_argument('--folder', help='enter input folder', default='/input')
args = parser.parse_args()
# Use arguments to perform requested action
path = args.folder

readFolder(path)