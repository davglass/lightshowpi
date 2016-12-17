Dav's LightShowPi Setup
=======================

![Board v2](lightshow-board.png?raw=true "Board v2")

Parts List
----------

* Raspberry Pi 3, Memory Card, Case, Power Cable
* [Male to Male Jumper Wires](http://a.co/eib2iWj)
* [SainSmart 8-Channel 5V Solid State Relay Module Board](http://a.co/4ZzxAcb)
* [8 Port Terminal Block](http://a.co/hs2jNlu)
* [3 spools 14 AWG solid wire](http://a.co/1X2Rdgd) (I used white, black and red)
* [3 electrical boxes](http://a.co/f1oh1xX)
* [Single Outlet Cover]( http://a.co/c8Ct4bO)
* [2 Double Outlet Covers](http://a.co/iz03UIc)
* [5 15amp Outlets](http://a.co/e8S6LzU)
* [Standard Computer Cable](http://a.co/7MdolDQ)


Wiring
------

![wiring](wiring.png?raw=true "wiring")

* Cut the end off the power cable that goes into the computer
* Strip it and attach a white and black to an outlet.
  * This outlet will be on all the time
  * Use this one to plug the Pi into
  * Put this into one of the boxes and use a single outlet
* Attach a white wire and run from the main outlet to another in the next box
* Then jump from top to bottom on all outlets across all three boxes
* Take a pair of needle nose pliers and snap the clip between the screws on the other side of the other 4 outlets
  * This will make the four outlets turn into 8 circuits
* Create a looped circuit on the terminal block like the photos
* Run a single red from each of the load sides of the outlets to the relay
* Run a black from the relay to the terminal block

Pins
----

Map the pins from the Pi to the Relays, [guide here](https://bitbucket.org/togiles/lightshowpi/src/master/config/defaults.cfg?fileviewer=file-view-default#defaults.cfg-104:127).

Usage
-----

Now, install Raspian on your pi, install [LightShowPi](http://lightshowpi.org/)

Config
------

* Set volume higher on boot
  * `sudo crontab -e`
  * `@reboot /usr/bin/amixer set PCM 95%`

`~/lights.cfg`

This is my default config, it fires up [`shairport-sync`](https://github.com/mikebrady/shairport-sync) and enables it as an AirPlay speaker. Then you 
can join it from any iOS device and stream music (Spotify in our case) directly into the lights display.

I also install the [`shairport-sync-metadata-reader`](https://github.com/mikebrady/shairport-sync-metadata-reader) module to grab the music
meta data while streaming..

```
[lightshow]
# We are using shairport-sync to setup an AirPlay Speaker
# that we will broadcast our music across, these are
# the settings needed..
mode = stream-in
stream_command_string = shairport-sync -v -o stdout
use_fifo = False
input_channels = 2
input_sample_rate = 44100

```

My Additions
------------

Copy `./bin` and `./api` into `/home/pi/`

`mkdir /home/pi/tmp`

Add `/home/pi/bin/boot.sh` to your `/etc/rc.local`

This will fire up the web based API server at: `http://raspberrypi.local:8888/`

Endpoints:

* `/show/start`
* `/show/stop`
* `/show/enable`
* `/show/disable`
* `/lights/on`
* `/lights/off`
* `/controller/cylon`
* `/controller/dance`
* `/controller/flash`
* `/controller/random_pattern`

You can (sort of) protect it with a JSON file: `/home/pi/.api.json`

```json
{
    "username": "foo",
    "password": "bar"
}
```

I added an IFTTT trigger to Alexa that points to my API so that I can turn them on and off with my Echo's.

[Additional Wiring Diagram from here](https://www.dropbox.com/s/tamanbq64qid30b/LightshowPi-Configandwire.docx?dl=0)

Content [Licensed BSD](LICENSE), use it as you will!
