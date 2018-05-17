#! python
# -*- coding: utf-8 -*-

import os
import argparse
import time
import app.analytics as analytics


#settings


#keep track of root directory
root_dir = os.path.abspath(os.curdir)

#help text
help = {
    'update': 'Get latest data from Google Analytics'
}


#set cmd line argument flags
parser = argparse.ArgumentParser(description='KLRN News Updates compiler and uploader')
parser.add_argument('-u', '--update', action='store_true', help=help['update'])
args = parser.parse_args()

def run(opts):
    if opts.update: print 'IT IS RUNNING'

run(args)