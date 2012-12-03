pnc_notify.py
==============

pnc_notify.py parses an icalendar-format file, finds post-natal checkup
appointments within a specified time in the future, and notifies the moms of
the upcoming appointment by SMS.

At the moment, it is assumed that it will be run silently from the cron, but a
"-d" flag sets verbose debugging output.

To run the code with the example file provided
--------------

With the sent.txt file generated from a previous run, the command

    ./pnc_notify.py 48 sent.txt example.ics -d

will give output (-d flag) showing who would be notified within 48 hours of an
appointment (48 hours before, assuming the cron job runs frequently).

Debugging will be easier if a phoney date is set, but this has not yet been
added to the command line.



