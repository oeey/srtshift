#!/usr/bin/env python

"""
SubRip Subtitle (.srt) Time Shift

Description: Sometimes subtitle files are off by a second or two.
    This will shift all time references forward or backwards
    by the time specified.

Usage: python srtshift.py <file.srt> <+/-shift_sec> [outfile.srt]

Param 1: srt file name
Param 2: time to shift in seconds (eg. -1.5 or 2.5)
Param 3: optional outfile to write to, else output to console
"""

__author__  = "Kenneth Burgener <kenneth@oeey.com>"
__date__    = "Feb 02, 2014"
__version__ = "1.0"
__license__ = "GPL"

import sys
import re
import decimal


def adj_time(adj_seconds, hours, minutes, seconds, milli):
    """
    Adjust time points forwards or backwards

    @param adj_seconds (float): seconds to adjust time
    @param hours (int): time hours
    @param minutes (int): time minutes
    @param seconds (int): time seconds
    @param milli (int): time milliseconds

    Example: adj_time(1.5, 0, 0, 1, 0) -> (0, 0, 2, 500)
    """

    # suffers from floating point issues, use Decimal instead
    #delta_milli = (abs(adj_seconds) - int(abs(adj_seconds))) * 1000.0 # suffers from floating point
    decimal.getcontext().prec = 3  # set decimal precision to 3 places
    delta_milli = int((decimal.Decimal(abs(adj_seconds)) - int(abs(adj_seconds))) * 1000)

    delta_sec = int(abs(adj_seconds))
    if adj_seconds > 0:
        milli += delta_milli
        seconds += delta_sec
        while milli >= 1000:
            milli -= 1000
            seconds += 1
        while seconds >= 60:
            seconds -= 60
            minutes += 1
        while minutes >= 60:
            minutes -= 60
            hours += 1
    elif adj_seconds < 0:
        milli -= delta_milli
        seconds -= delta_sec
        while milli < 0:
            milli += 1000
            seconds -= 1
        while seconds < 0:
            seconds += 60
            minutes -= 1
        while minutes < 0:
            minutes += 60
            hours -= 1
    if hours < 0:
        return 0, 0, 0, 0
    return hours, minutes, seconds, milli


def run():
    """ Process command line parameters and adjust .srt file """

    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print "Usage: python %s <file.srt> <+/-shift_sec> [outfile.srt]" % sys.argv[0]
        print "Example: python %s movie.srt 1.5 > movie_out.srt" % sys.argv[0]
        sys.exit(1)

    infile = sys.argv[1]
    shift_sec = sys.argv[2]

    if len(sys.argv) == 4:
        outfile = sys.argv[3]
        outfile_handle = open(outfile, 'w')
    else:
        outfile = None

    with open(infile) as f:
        for line in f:
            match = re.findall('([0-9]+):([0-9]+):([0-9]+),([0-9]+) --> ([0-9]+):([0-9]+):([0-9]+),([0-9]+)', line)
            if match:
                match = match[0]
                start_hour = int(match[0])
                start_minutes = int(match[1])
                start_sec = int(match[2])
                start_milli = int(match[3])
                end_hour = int(match[4])
                end_minutes = int(match[5])
                end_sec = int(match[6])
                end_milli = int(match[7])

                start_hour, start_minutes, start_sec, start_milli = \
                    adj_time(float(shift_sec), start_hour, start_minutes, start_sec, start_milli)
                end_hour, end_minutes, end_sec, end_milli = \
                    adj_time(float(shift_sec), end_hour, end_minutes, end_sec, end_milli)

                if outfile:
                    outfile_handle.write("{0:02}:{1:02}:{2:02},{3:03} --> {4:02}:{5:02}:{6:02},{7:03}\n".format(
                        start_hour, start_minutes, start_sec, start_milli,
                        end_hour, end_minutes, end_sec, end_milli))
                else:
                    print "{0:02}:{1:02}:{2:02},{3:03} --> {4:02}:{5:02}:{6:02},{7:03}".format(
                        start_hour, start_minutes, start_sec, start_milli,
                        end_hour, end_minutes, end_sec, end_milli)

            else:
                if outfile:
                    outfile_handle.write(line.strip() + "\n")
                else:
                    print line.strip()

if __name__ == "__main__":
    run()
