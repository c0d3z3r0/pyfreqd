#!/usr/bin/env python3

# pyfreqd - CPUfreq userpace governor for overclocked Radxa Rock written in python
# Copyright (C) 2016  Michael Niewöhner <foss@mniewoehner.de>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from psutil import cpu_percent
import time
import logging
import argparse


CPUFREQ_PATH = '/sys/devices/system/cpu/cpufreq/policy0/'

freqs = [
    {'thresh': 70, 'freq':  816000, 'timeout': 30, 'cooltime': 4*60 },
    {'thresh': 55, 'freq': 1008000, 'timeout': 35, 'cooltime': 4*60 },
    {'thresh': 40, 'freq': 1200000, 'timeout': 45, 'cooltime': 4*60 },
    {'thresh': 20, 'freq': 1416000, 'timeout': 60, 'cooltime': 4*60 },
    {'thresh':  0, 'freq': 1920000, 'timeout':  0, 'cooltime':    0 },
]

def setup():
    with open(CPUFREQ_PATH + "scaling_governor", "w") as f:
        f.write('userspace')
    with open(CPUFREQ_PATH + "scaling_min_freq", "w") as f:
        f.write(str(freqs[0]['freq']))
    with open(CPUFREQ_PATH + "scaling_max_freq", "w") as f:
        f.write(str(freqs[-1]['freq']))

def get_freq():
    with open(CPUFREQ_PATH + "scaling_cur_freq", "r") as f:
        return int(f.read().strip())

def set_freq(freq):
    with open(CPUFREQ_PATH + "scaling_setspeed", "w") as f:
        return f.write(str(freq))

def get_usage():
    usage = 0
    for i in range(0, 5):
        usage += cpu_percent()
        time.sleep(0.2)
    return int(usage / 5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debugging')
    args = parser.parse_args()

    log = logging.getLogger('pyfreqd')
    loghandler = logging.StreamHandler()
    log.addHandler(loghandler)
    log.setLevel(logging.DEBUG if args.debug else logging.WARNING)

    setup()
    set_freq(freqs[-1]['freq'])
    log.debug('Set initial speed to %s' % freqs[-1]['freq'])

    while True:
        usage = get_usage()
        new_freq = next(filter(lambda freq: freq['thresh'] <= usage, freqs))
        if not new_freq['timeout']:
            #log.debug('Below minimum threshold, no change.')
            continue
        # wait for timeout
        log.debug('Usage %s above threshold %s. Cooldown freq is %s.' %
                  (usage, new_freq['thresh'], new_freq['freq']))
        log.debug('Waiting %s seconds for timeout.' % new_freq['timeout'])
        timeout = time.time() + new_freq['timeout']
        while time.time() < timeout:
            # check rising or sinking usage
            usage = get_usage()
            step_freq = next(filter(lambda freq: freq['thresh'] <= usage, freqs))
            # higer usage: step down
            if step_freq['freq'] < new_freq['freq']:
                log.debug('Usage at %s. Current freq is %s.' % (usage, get_freq()))
                log.debug('Step down to %s.' % step_freq['freq'])
                set_freq(step_freq['freq'])
                new_freq = step_freq
            # lower usage: step up
            elif step_freq['freq'] > new_freq['freq']:
                log.debug('Usage at %s. Current freq is %s.' % (usage, get_freq()))
                log.debug('Step up to %s.' % step_freq['freq'])
                set_freq(step_freq['freq'])
                new_freq = step_freq
        # cool down
        log.debug('Now cooling down for %s seconds at %s.' %
                  (new_freq['cooltime'], new_freq['freq']))
        set_freq(new_freq['freq'])
        timeout = time.time() + new_freq['cooltime']
        while time.time() < timeout:
            # check rising usage; don't allow to step up in cooling phase
            usage = get_usage()
            step_freq = next(filter(lambda freq: freq['thresh'] <= usage, freqs))
            # higer usage: step down
            if step_freq['freq'] < new_freq['freq']:
                log.debug('Usage at %s. Current freq is %s.' % (usage, get_freq()))
                log.debug('Step down to %s.' % step_freq['freq'])
                set_freq(step_freq['freq'])
                new_freq = step_freq
        # switch back
        log.debug('Switching back to %s.' % freqs[-1]['freq'])
        set_freq(freqs[-1]['freq'])
