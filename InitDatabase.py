import os
import django
import argparse
import sys

parser = argparse.ArgumentParser(description="Populate the database with initial values")
parser.add_argument('--mode', nargs='?', const=1, type=str, default='debug', help='debug/production')
parser.add_argument('--create-dummy-data', dest='createDummyData', action='store_true', help='if activated dummy data is generated') #doesnt do anything yet
parser.set_defaults(createDummyData=False)
DUMMY, MODE = parser.parse_args().createDummyData, parser.parse_args().mode

if MODE not in ["debug", "production"]:
    sys.exit(1)

if MODE == 'debug':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'FootlooseAfdansenApp.settings_development'
elif MODE == 'production':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'FootlooseAfdansenApp.settings'

django.setup()

from afdansen.models import *

print('Saving dance types')
for d in ['latin', 'ballroom']:
    for n in ['brons', 'zilver', 'zilverster', 'goud', 'topklasse']:
        print('{}_{}'.format(d, n))
        obj, created = Dance.objects.get_or_create(Name='{}_{}'.format(d, n))

for d in ['salsa', 'zouk']:
    for n in [1, 2, 3]:
        print('{}_{}'.format(d, n))
        obj, created = Dance.objects.get_or_create(Name='{}_{}'.format(d, n))

for n in [2, 3, 4, 11, 14, 16, 19, 23, 25, 34, 37, 38, 41, 70, 73, 82, 88, 102, 106, 121,
                                      135, 136, 140, 146, 148, 150, 151, 162, 163, 164, 166, 167, 174, 180]:
    missing = MissingBackNumber()
    missing.Number = n
    missing.save()
