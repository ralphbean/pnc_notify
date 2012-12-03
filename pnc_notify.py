#!/usr/bin/env python

# Script to notify mothers of upcoming post-natal checkups.
# Peace Corps Innovation Challenge 
# http://innovationchallenge.peacecorps.gov/idea/51
# https://github.com/adamhayes/pnc_notify

# Assumptions:  The calendar time-zone is the local time-zone.  It is not clear
# how this will function if it is not.

#################################
# Geographically Local Settings #
#################################
                                #
MIN_PHONE_NUMBER_DIGITS = 10    #
MAX_PHONE_NUMBER_DIGITS = 10    #
                                #
#################################

import datetime
from dateutil import relativedelta
from dateutil import rrule
from dateutil import parser
import time
from icalendar import Calendar, Event
import commands
import sys           # for sys.argv to run non-interactively from the command-line.
import pickle


################################################################################
# Parse the command line args (crude).                                         #
################################################################################

command_line_args = sys.argv[1:]

if not len(command_line_args) >= 3:
    print "Usage:"
    print "  python pnc_notify.py  delta-t  already-notified-file-name  ics-calendar-file-name"
    print "  where delta-t is in hours, e.g."
    print "  python pnc_notify.py 24 notified.txt my_calendar.ics"
    quit()

# Need a minimum of 3 arguments, in this order:
NOTIFY_DELTA_T, ALREADY_NOTIFIED_FILE_NAME, ICS_FILE_NAME = command_line_args[:3]
# where notify_delta_t is in hours.  Moms will be notified once at most this
# many hours before the appointment.

################################################################################
# Things for debugging only                                                    #
################################################################################
import pprint                                                                  #
                                                                               # 
# A debugging flag on the command line turns on extra output to stdout.        #
if "-d" in command_line_args:                                                  #
    DEBUGGING = True                                                           #
else:                                                                          #
    DEBUGGING = False                                                          #
                                                                               # 
def debug_print(thing):                                                        #
    if DEBUGGING:                                                              #
         print "DEBUGGING: "                                                   #
         pprint.pprint(thing)                                                  #
                                                                               # 
################################################################################


# Create a relativedelta instance representing this NOTIFY_DELTA_T.
NOTIFY_RELATIVE_DELTA = relativedelta.relativedelta(hours=int(NOTIFY_DELTA_T))

################################################################################
# Setup for the "relativedelta" time calculations.                             #
################################################################################

# A type object of a datetime.datetime for comparison to other types.
DATETIME_TYPE = type(datetime.datetime(2000,1,1))

ZERO_DELTA = relativedelta.relativedelta(hours=0)
ONE_HOUR_DELTA = relativedelta.relativedelta(hours=1)

# Get the current date and time.  With no arguments, time.ctime() returns the
# local time as a string.
current_time = time.ctime()
current_time_obj = parser.parse(commands.getoutput("date"))
current_date_only = datetime.date(current_time_obj.year, current_time_obj.month, current_time_obj.day)

################################################################################
################################################################################

def parse_phone(description):
    """Parses a description field of an ical ics event to find a line with a phone number on it.

        DESCRIPTION:This is my first line of description.\nThis is the second.\nher
         e is a phone number on the third 585 555 5555 blah blah on phone number lin
         e\nphone: 123 456 7980\nand one last line

        "\n" is really a \ followed by "n".

    """

    desc_lines = description.split("\n")

    # Check each line for a phone number.  It should be on a line by itself!
    for line in desc_lines:
        # Change to lower case.
        line = line.lower()
        # Strip whitespace.
        line = line.strip()
        # Does the line start with "phone" or "telephone"
        if line.startswith("phone") or line.startswith("telephone"):
            # This could be a phone number to contact by SMS.
        
            phone_number = ""
            for one_character in line:
                if one_character.isdigit():
                    phone_number += one_character

            if len(phone_number) >= MIN_PHONE_NUMBER_DIGITS and \
               len(phone_number) <= MAX_PHONE_NUMBER_DIGITS:
                # This is possibly a correct phone number.  Return it.
                return phone_number

    # No phone numbers found.
    return None


def create_message(ical_entry):
    """This creates message text and returns it, along with the SMS address.

    """
    
    pass

    return []  # [message_text, sms_address]

class logger:
    """Reads/writes IDs of appointments already sent to moms.

    File format is expected to be 

        [{'sent date': datetime.date(2012, 12, 2), 'appointment date': datetime.datetime(2012, 12, 11, 15, 0, tzinfo=<UTC>), 'phone number': u'1234567980', 'UID': vText(u'm2jkmrmn81rtk0kk7m0khdpcr4@google.com')},...]

        {"UID":"some id string", "phone number":5855551234, "appointment date":"2012-11-5 09:15:00", "sent date":"2012-11-4 12:00:00"}
        ...

    which will be read as a list of dicts.

    """

    def __init__(self,file_name):
        """ Open/create the log file, and read all UIDs from it.

        This now uses pickle for simplicity in case the data format is changed.

        """

        try:
            pickle_file = open(ALREADY_NOTIFIED_FILE_NAME, "rb")
            self.already_notified = pickle.load(pickle_file)
            pickle_file.close()
            debug_print("====>" + str(self.already_notified))

        except:
            # File did not exist.  Create an empty file and return an empty list.
            try:
                f = open(file_name, "wb")
                self.already_notified = []
                f.close()
            except:
                self.already_notified = []


    def get_was_notified(self,UID):
        """Checks the log for ical UID and returns True/False.

        UID must be a string, and is expected to be the UID field in an ical event.

        """

        for entry in self.already_notified:
            if entry["UID"] == UID:
                return True

        return False

    def set_was_notified(self, UID, phone_number, appointment_date, sent_date):
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

            self.already_notified.append(entry)

            return 0

        except:

            return -1

    def prune_old_entries(self):
        """Delete entries from the past, which wouldn't get sent in any case.

        Look for entries in this format (below) where the date or datetime of
        the appointment are in the past.  Depending on whether the user put a
        time in the ical data or not, this may be a datetime.date or a
        datetime.datetime.
        
        [{'sent date': datetime.date(2012, 12, 2), 'appointment date': datetime.datetime(2012, 12, 11, 15, 0, tzinfo=<UTC>), 'phone number': u'1234567980', 'UID': vText(u'm2jkmrmn81rtk0kk7m0khdpcr4@google.com')},...]
        """

        new_notified_list = []
        for entry in self.already_notified:
            checkup_time = entry["appointment date"]
            if type(checkup_date) == DATETIME_TYPE: 
                delta_t = relativedelta.relativedelta(checkup_date, current_time_obj)
            else:
                delta_t = relativedelta.relativedelta(checkup_date, current_date_only)
            if not delta_t < ZERO_DELTA:
                # It is not in the past.  Put it in the new list.
                new_notified_list.append(entry)
        # Replace the original list with the new one.
        self.already_notified = new_notified_list

        return 0



    def write_out(self):
        """Write the updated entries to the log file.

        """

        # Get rid of the entries from the past.
        self.prune_old_entries()

        # Write remaining entries to the file.
        try:
            pickle_file = open(ALREADY_NOTIFIED_FILE_NAME, "wb")
            pickle.dump(self.already_notified, pickle_file)
            pickle_file.close()
        except:
            pickle_file.close()
            return -1

        pickle_file.close()
        return 0



################################################################################
# CRON SCRIPT                                                                  #
################################################################################

# Create a logger, which will read a log file if it exists.
Logger = logger(ALREADY_NOTIFIED_FILE_NAME)

debug_print("Already notified: ")
debug_print(Logger.already_notified)

# Read the ical-standard file.
pnc_cal = Calendar.from_ical(open(ICS_FILE_NAME,'rb').read())

for component in pnc_cal.walk():

    # Get the start date of this event (date of check-up); check-ups are probably one day long.
    debug_print("--------------------------------------------------------------------------------\n")
    if component.name == "VEVENT": 
        pnc_date_object = component['DTSTART']

        # This is either a datetime.datetime object with a time, or a
        # datetime.date object that must be converted to datetime.date
        checkup_date = pnc_date_object.dt  

        checkup_time = checkup_date.timetuple()

        debug_print("checkup_time: " + str(checkup_time))

        if type(checkup_date) == DATETIME_TYPE: 
            delta_t = relativedelta.relativedelta(checkup_date, current_time_obj)
        else:
            delta_t = relativedelta.relativedelta(checkup_date, current_date_only)
            
        # ISSUE: relativedelta issue:  If the relativedelta has no hours in it
        # (hours=0), then it cannot be compared to one with nonzero hours.  See
        # here:
        # http://stackoverflow.com/questions/11704341/comparing-dateutil-relativedelta
        # Hence, the second "if" below.

        if delta_t > ZERO_DELTA:
            if delta_t.hours == 0:
                # The "hours" attribute is identically 0.
                temp_delta_t               = delta_t               + ONE_HOUR_DELTA 
                temp_NOTIFY_RELATIVE_DELTA = NOTIFY_RELATIVE_DELTA + ONE_HOUR_DELTA
                should_notify = temp_delta_t > temp_NOTIFY_RELATIVE_DELTA 
            else:
                # The time difference contains non-zero hours attribute.
                should_notify = delta_t > NOTIFY_RELATIVE_DELTA 

        if should_notify:
            debug_print("This appointment is within the time window to notify.")
        else:
            debug_print("This appointment is NOT within the time window to notify.")

        if should_notify:

            # Get the calendar event identifier to compare with notifications already sent.
            UID = component['UID']
            debug_print("UID: " + str(UID))

            # Check the entries from the already-notified file, and eliminate any that have already been notified.
            was_notified = Logger.get_was_notified(UID)

            #was_notified = False # Debugging

            if not was_notified:
                # Get the summary.  On google calendar, this is the event title.
                summary = component['SUMMARY']
                debug_print("SUMMARY:")
                debug_print(summary)

                # Get the event description, which will contain the phone
                # number and message primitives.  These primitives will be used
                # to compose the message.  (The complete message itself does
                # not need to be typed in the calendar; it will be constructed
                # from these primitives.)
                description = component['DESCRIPTION']

                # The description should contain items formatted as 
                # Example "DESCRIPTION" line:  (line breaks are coded as backslash-n.)
                # DESCRIPTION:Get required number of order forms from Connie.\n(Do I h
                #  ave them in my files or on the dept. website?)

                # Get the phone number.  At the moment, the phone number should
                # be on a separate line.  Not sure about using other fields in
                # the ics format, such as guests, because some apps use these
                # differently. (?)

                phone_number = parse_phone(description) # Returned as a string.
                debug_print("phone number found: " + str(phone_number))

                if not phone_number == None:

                    # Make a message.
                    the_message = create_message(component)

                    # Send the message to the mom. (Twilio?)
                    debug_print("SENDING MESSAGE NOW.")
                    #Sender.send(the_message)

                    # Add this appointment ID to the already-notified file
                    Logger.set_was_notified(UID, phone_number, checkup_date, current_date_only)

            else:
                # Already notified in a previous execution.
                pass
                debug_print("Already notified mom about this checkup.  NOT SENDING.")


        if DEBUGGING:
            raw_input("debugging: press enter")

debug_print("Finished scanning calendar.")
debug_print(Logger.already_notified)
#Logger.prune_old_entries()  # NOT NECESSARY; it is done in the write_out.
# Write the updated file of moms who were notified already.
Logger.write_out()
debug_print("Already notified: ")
debug_print(Logger.already_notified)



