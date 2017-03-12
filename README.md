# libhbtrash
functions for parsing the Entsorgung Kommunal Abfallkalender

## Install

    git clone https://github.com/bitstacker/libhbtrash.git
    virtualenv -p /usr/bin/python3 libhbtrash/
    cd libhbtrash
    source bin/activate
    pip install -r requirements.txt


## Usage

    from libhbtrash.libhbtrash import Muellplan
    m = Muellplan()
    print(m.getIcal(street, number, other, alarm))

