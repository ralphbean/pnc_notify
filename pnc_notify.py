#!/usr/bin/env python

from dateutil import relativedelta
from dateutil import rrule
from dateutil import parser

from icalendar import Calendar, Event

import commands
import os
import sys           # for sys.argv to run non-interactively from the command-line.

# Read the ical-standard file.


# Collect all entries that are within the desired delta-t.


# Check the already-notified file, and eliminate any that have already been notified.


# Notify each mom by SMS.


# Clean up the already-notified file by deleting entries for appointments that are in the past.





