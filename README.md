# pyfreqd

CPUfreq userpace governor for overclocked Radxa Rock written in python.

## Installation

~~~sh
aptitude install python3-psutil
cp pyfreqd.py /usr/local/sbin/pyfreqd
chmod +x /usr/local/sbin/pyfreqd
cp pyfreqd.service /etc/systemd/system/
systemctl enable pyfreqd.service
systemctl start pyfreqd.service
~~~

## License

Copyright (C) 2016 Michael Niewöhner

This is open source software, licensed under GPLv2. See the file LICENSE for details.
