import sys
import datetime
import sys
from _datetime import datetime
time_tuple = ( 2021, # Year
                  11, # Month
                  15, # Day
                  1, # Hour
                 47, # Minute
                  0, # Second
                  0, # Millisecond
              )


def _linux_set_time(time_tuple):
    import subprocess
    import shlex

    time_string = datetime(*time_tuple).isoformat()

    subprocess.call(shlex.split("timedatectl set-ntp false"))  # May be necessary
    subprocess.call(shlex.split("sudo date -s '%s'" % time_string))
    subprocess.call(shlex.split("sudo hwclock -w"))


if __name__=="__main__":
    _linux_set_time(time_tuple)