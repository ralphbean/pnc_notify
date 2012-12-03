pnc_notify.py
==============

This is a long file...

pnc_notify.py parses an icalendar-format file, finds post-natal checkup
appointments within a specified time in the future, and notifies the moms of
the upcoming appointment by SMS.

It keeps track of which moms were already notified in an already-notified file,
so that they will not be notified again.  Once an appointment is in the past,
it is removed from the already-notified file to avoid making a large file to
search.

At the moment, it is assumed that it will be run silently from the cron, but a
"-d" flag sets verbose debugging output.

Running and testing
--------------

Debugging will be easier if a phoney date is set, but this has not yet been
added to the command line.

With the sent.txt file generated from a previous run, the command

    ./pnc_notify.py 48 sent.txt example.ics -d

will give output (-d flag) showing who would be notified once within 48 hours
of an appointment (48 hours before, assuming the cron job runs frequently).

If the sent.txt file is present, moms who were already notified will not be
notified again.  (These moms are stored in the sent.txt file in a pickle
format.)  IF the sent.txt file is deleted, then all moms will be notified in
the selected window.

Debugging examples
----------------

With the current date as Dec 3, 2012 and the sent.txt and example.ics files
present as in the repo, executing

    ./pnc_notify.py 3000 sent.txt example.ics -d

(arbitrarily large 3000 hours-ahead notification) will give the following long
output, while deleting the sent.txt file will give similar output with messages 

'Already notified mom about this checkup.  NOT SENDING.'

replaced with 

'SENDING MESSAGE NOW.'

Here is the long output:

hayes@Sobchak:~/sms_reminder$ ./pnc_notify.py 3000 sent.txt example.ics -d
DEBUGGING: 
"====>[{'appointment date': datetime.datetime(2012, 12, 4, 18, 0, tzinfo=<UTC>), 'sent date': datetime.date(2012, 12, 3), 'UID': vText(u'51438ik2u4oss2e7fkprhingtg@google.com'), 'phone number': u'2938397564'}, {'appointment date': datetime.datetime(2012, 12, 4, 17, 0, tzinfo=<UTC>), 'sent date': datetime.date(2012, 12, 3), 'UID': vText(u'v2learqro0b5884lrudodjolgc@google.com'), 'phone number': u'1234567890'}, {'appointment date': datetime.datetime(2012, 12, 11, 15, 0, tzinfo=<UTC>), 'sent date': datetime.date(2012, 12, 3), 'UID': vText(u'm2jkmrmn81rtk0kk7m0khdpcr4@google.com'), 'phone number': u'1234567980'}]"
DEBUGGING: 
'Already notified: '
DEBUGGING: 
[{'UID': vText(u'51438ik2u4oss2e7fkprhingtg@google.com'),
'appointment date': datetime.datetime(2012, 12, 4, 18, 0, tzinfo=<UTC>),
'phone number': u'2938397564',
'sent date': datetime.date(2012, 12, 3)},
{'UID': vText(u'v2learqro0b5884lrudodjolgc@google.com'),
'appointment date': datetime.datetime(2012, 12, 4, 17, 0, tzinfo=<UTC>),
'phone number': u'1234567890',
'sent date': datetime.date(2012, 12, 3)},
{'UID': vText(u'm2jkmrmn81rtk0kk7m0khdpcr4@google.com'),
'appointment date': datetime.datetime(2012, 12, 11, 15, 0, tzinfo=<UTC>),
'phone number': u'1234567980',
'sent date': datetime.date(2012, 12, 3)}]
DEBUGGING: 
'--------------------------------------------------------------------------------\n'
DEBUGGING: 
'--------------------------------------------------------------------------------\n'
DEBUGGING: 
'checkup_time: time.struct_time(tm_year=2012, tm_mon=12, tm_mday=20, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=355, tm_isdst=-1)'
DEBUGGING: 
'This appointment is NOT within the time window to notify.'
debugging: press enter
DEBUGGING: 
'--------------------------------------------------------------------------------\n'
DEBUGGING: 
'checkup_time: time.struct_time(tm_year=2012, tm_mon=12, tm_mday=4, tm_hour=18, tm_min=0, tm_sec=0, tm_wday=1, tm_yday=339, tm_isdst=0)'
DEBUGGING: 
'This appointment is within the time window to notify.'
DEBUGGING: 
'UID: 51438ik2u4oss2e7fkprhingtg@google.com'
DEBUGGING: 
'Already notified mom about this checkup.  NOT SENDING.'
debugging: press enter
DEBUGGING: 
'--------------------------------------------------------------------------------\n'
DEBUGGING: 
'checkup_time: time.struct_time(tm_year=2012, tm_mon=12, tm_mday=4, tm_hour=17, tm_min=0, tm_sec=0, tm_wday=1, tm_yday=339, tm_isdst=0)'
DEBUGGING: 
'This appointment is within the time window to notify.'
DEBUGGING: 
'UID: v2learqro0b5884lrudodjolgc@google.com'
DEBUGGING: 
'Already notified mom about this checkup.  NOT SENDING.'
debugging: press enter
DEBUGGING: 
'--------------------------------------------------------------------------------\n'
DEBUGGING: 
'checkup_time: time.struct_time(tm_year=2012, tm_mon=11, tm_mday=28, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=2, tm_yday=333, tm_isdst=-1)'
DEBUGGING: 
'This appointment is NOT within the time window to notify.'
debugging: press enter
DEBUGGING: 
'--------------------------------------------------------------------------------\n'
DEBUGGING: 
'checkup_time: time.struct_time(tm_year=2012, tm_mon=12, tm_mday=11, tm_hour=15, tm_min=0, tm_sec=0, tm_wday=1, tm_yday=346, tm_isdst=0)'
DEBUGGING: 
'This appointment is within the time window to notify.'
DEBUGGING: 
'UID: m2jkmrmn81rtk0kk7m0khdpcr4@google.com'
DEBUGGING: 
'Already notified mom about this checkup.  NOT SENDING.'
debugging: press enter
DEBUGGING: 
'Finished scanning calendar.'
DEBUGGING: 
[{'UID': vText(u'51438ik2u4oss2e7fkprhingtg@google.com'),
'appointment date': datetime.datetime(2012, 12, 4, 18, 0, tzinfo=<UTC>),
'phone number': u'2938397564',
'sent date': datetime.date(2012, 12, 3)},
{'UID': vText(u'v2learqro0b5884lrudodjolgc@google.com'),
'appointment date': datetime.datetime(2012, 12, 4, 17, 0, tzinfo=<UTC>),
'phone number': u'1234567890',
'sent date': datetime.date(2012, 12, 3)},
{'UID': vText(u'm2jkmrmn81rtk0kk7m0khdpcr4@google.com'),
'appointment date': datetime.datetime(2012, 12, 11, 15, 0, tzinfo=<UTC>),
'phone number': u'1234567980',
'sent date': datetime.date(2012, 12, 3)}]
DEBUGGING: 
'Already notified: '
DEBUGGING: 
[{'UID': vText(u'51438ik2u4oss2e7fkprhingtg@google.com'),
'appointment date': datetime.datetime(2012, 12, 4, 18, 0, tzinfo=<UTC>),
'phone number': u'2938397564',
'sent date': datetime.date(2012, 12, 3)},
{'UID': vText(u'v2learqro0b5884lrudodjolgc@google.com'),
'appointment date': datetime.datetime(2012, 12, 4, 17, 0, tzinfo=<UTC>),
'phone number': u'1234567890',
'sent date': datetime.date(2012, 12, 3)},
{'UID': vText(u'm2jkmrmn81rtk0kk7m0khdpcr4@google.com'),
'appointment date': datetime.datetime(2012, 12, 11, 15, 0, tzinfo=<UTC>),
'phone number': u'1234567980',
'sent date': datetime.date(2012, 12, 3)}]
hayes@Sobchak:~/sms_reminder$ 


