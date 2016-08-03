# libhbtrash
functions for parsing the Entsorgung Kommunal Abfallkalender

## Install

<code>
virtualenv -p /usr/bin/python3 libhbtrash/
cd libhbtrash
source bin/activate
pip install -r requirements.txt
</code>

## Usage

<code>
from libhbtrash.libhbtrash import Muellplan

m = Muellplan()
print(m.getIcal(street, number, other, alarm))

</code>
