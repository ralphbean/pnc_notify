#!/usr/bin/env python

# Script to notify mothers of upcoming post-natal checkups.
# Peace Corps Innovation Challenge 
# http://innovationchallenge.peacecorps.gov/idea/51

# Assumptions:  The calendar time-zone is the local time-zone.

import datetime

# A type object of a datetime.datetime for comparison to other types.
DATETIME_TYPE = type(datetime.datetime(2000,1,1))
UTC = datetime.tzinfo()

from dateutil import relativedelta
from dateutil import rrule
from dateutil import parser

import time

from icalendar import Calendar, Event

import commands
import os
import sys           # for sys.argv to run non-interactively from the command-line.

def create_message(ical_entry):
    """This creates message text and returns it, along with the SMS address.

    """
    
    pass

    return # [message_text, sms_address]

# Parse the command line args (crude).
command_line_args = sys.argv[1:]

if not len(command_line_args) == 3:
    print "Usage:"
    print "  python pnc_notify.py  delta-t  already-notified-file-name  ics-calendar-file-name"
    print "  where delta-t is in hours, e.g."
    print "  python pnc_notify.py 24 notified.txt my_calendar.ics"
    quit()

# Need a minimum of 3 arguments, in this order:
NOTIFY_DELTA_T, ALREADY_NOTIFIED_FILE_NAME, ICS_FILE_NAME = command_line_args
# where notify_delta_t is in hours.  Moms will be notified once at most this
# many hours before the appointment.

# Create a relativedelta instance representing this NOTIFY_DELTA_T.
NOTIFY_RELATIVE_DELTA = relativedelta.relativedelta(hours=int(NOTIFY_DELTA_T))
ZERO_DELTA = relativedelta.relativedelta(hours=0)
ONE_HOUR_DELTA = relativedelta.relativedelta(hours=1)

# Get the current date and time.  With no arguments, time.ctime() returns the
# local time as a string.
current_time = time.ctime()

current_time_obj = parser.parse(commands.getoutput("date"))
current_date_only = datetime.date(current_time_obj.year, current_time_obj.month, current_time_obj.day)

class logger:
    """Reads/writes IDs of appointments already sent to moms.

    File format is expected to be 

        {"UID":"some id string", "phone number":5855551234, "appointment date":"2012-11-5 09:15:00", "sent date":"2012-11-4 12:00:00"}
        ...

    which will be read as a list of dicts.

    """

    def __init__(self,file_name):
        """ Open/create the log file, and read all UIDs from it.

        """

        try:
            f = open(file_name, "r")
            self.uid_file_entries = f.readlines()

        except:
            # File did not exist.  Create an empty file and return an empty list.
            f = open(file_name, "w")

        f.close()

    def get_was_notified(self,UID):
        """Checks the log for ical UID and returns True/False.

        UID must be a string, and is expected to be the UID field in an ical event.

        """

        for entry in self.uid_file_entries:
            if entry["UID"] == UID:
                return True

        return False

    def set_was_notified(self,UID,phone_number, appointment_date, sent_date):
        """Adds this notification to the notified-file, 
        
        {"UID":"some id string", "phone number":5855551234, "appointment date":"2012-11-5 09:15:00", "sent date":"2012-11-4 12:00:00"}

        Returns
             0 - success
            -1 - fail
        
        """

        try:

            entry = { \
                     "UID" : UID, \
                     "phone number" : phone_number, \
                     "appointment date" : appointment_date, \
                     "sent date" : sent_date, \
                    }

            self.uid_file_entries.append(entry)

            return 0

        except:

            return -1



# Read the ical-standard file.
pnc_cal = Calendar.from_ical(open('example_cal.ics','rb').read())

# Read the file containing appointments for which the mom was already notified.
read_already_notified_file(ALREADY_NOTIFIED_FILE_NAME)

for component in pnc_cal.walk():
    #print component.name 
    # VEVENT({'STATUS': vText(u'CONFIRMED'), 'ATTENDEE': vCalAddress('mailto:1avsv0nep20o8p8e3t70r0hguk@group.calendar.google.com'), 'UID': vText(u'terh697is5qaobrkig1jif2ja8@google.com'), 'CREATED': <icalendar.prop.vDDDTypes instance at 0xd24098>, 'SEQUENCE': 0, 'TRANSP': vText(u'OPAQUE'), 'DTSTAMP': <icalendar.prop.vDDDTypes instance at 0xd11ef0>, 'SUMMARY': vText(u'dr appt.'), 'LAST-MODIFIED': <icalendar.prop.vDDDTypes instance at 0xd240e0>, 'LOCATION': vText(u''), 'DTEND': <icalendar.prop.vDDDTypes instance at 0xd11ea8>, 'DTSTART': <icalendar.prop.vDDDTypes instance at 0xd11e60>, 'DESCRIPTION': vText(u'call asap if I need to cancel')}) <class 'icalendar.cal.Event'><====
    #  a 2012-06-11 20:00:00+00:00

    # Get the start date of this event (date of check-up); check-ups are probably one day long.
    print "--------------------------------------------------------------------------------\n"
    # print "\n\n" + str(component) + " " + str(type(component)) + "<===="
    # If this is a calendar event, not timezone info, etc...
    if component.name == "VEVENT": 
        #for item in component:
            #print item
        # raw_input(dir(component))
        pnc_date_object = component['DTSTART']
        # print dir(pnc_date_object)

        # This is either a datetime.datetime object with a time, or a
        # datetime.date object that must be converted to datetime.date
        checkup_date = pnc_date_object.dt  

        checkup_time = checkup_date.timetuple()

        print "checkup_time: ", checkup_time 
        if type(checkup_date) == DATETIME_TYPE: 
            delta_t = relativedelta.relativedelta(checkup_date, current_time_obj)
            print "A"
        else:
            delta_t = relativedelta.relativedelta(checkup_date, current_date_only)
            print "B"
            
        # relativedelta issue:  If the relativedelta has no hours in it
        # (hours=0), then it cannot be compared to one with nonzero hours.  See
        # here:
        # http://stackoverflow.com/questions/11704341/comparing-dateutil-relativedelta
        # Hence, the first "if":

        if delta_t > ZERO_DELTA:
            if delta_t.hours == 0:
                temp_delta_t               = delta_t               + ONE_HOUR_DELTA 
                temp_NOTIFY_RELATIVE_DELTA = NOTIFY_RELATIVE_DELTA + ONE_HOUR_DELTA
                should_notify = temp_delta_t < temp_NOTIFY_RELATIVE_DELTA 
            else:
                # The time difference contains non-zero hours attribute.
                should_notify = delta_t < NOTIFY_RELATIVE_DELTA 

        if should_notify:
            print "SHOULD NOTIFY"

            # Get the calendar event identifier to compare with notifications already sent.
            uid = component['UID']
            print uid


            # Check the entries from the already-notified file, and eliminate any that have already been notified.

            raw_input("press enter")
        # Notify the mom.

        # Make a message.
        create_message(component)

        # Send the message (Twilio?)

        # Add this appointment ID to the already-notified file

        already_notified_IDs.append(appointment_ID)

        # Clean up the already-notified file:  Delete entries for appointments
        # in the past, and rewrite the file.



# Notify each mom by SMS.


# Clean up the already-notified file by deleting entries for appointments that are in the past.





