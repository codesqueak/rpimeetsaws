# Power 

Powering the project is approached from two angles.  Sufficient power needs to be generated in worst case scenarios (Winter) and power usage needs
to be minimized to help meet the power budget.

## Power Generation & Storage

### Solar Panel

[Huge 6V 6W Solar panel](https://www.adafruit.com/product/1525)

This panel is capable of supply sufficient power to both supply the Raspberry Pi and charge the battery for periods of darkness. Maximum output
closely matches the maximum charge rate the charge controller can deliver (Approx. 1000mA).  The panel is also waterproof, scratch resistant, and UV resistant 
which makes it ideal for outside usage.

### Solar Lithium Ion/Polymer Charger

[USB / DC / Solar Lithium Ion/Polymer charger - v2](https://www.adafruit.com/product/390)

This charger is a simple solution to building a battery / solar power source.  See Adafruit for full details.

The device has one unfortunate characteristic which is that when on solar, the output voltage can rise to that of the panel.  This then requires
some form of regulation if a stable 5V supply is required.  The output volatage range is between battery voltage (3.7V) and the panel ouptut (6V).

### DC/DC Converter

[PowerBoost 1000 Basic - 5V USB Boost ](https://www.adafruit.com/product/2030)

The output of the charger needs to be used to produce a steady 5V output for the Raspberry Pi. This device is a simple solution to that problem.

Notes:

* The output is actually 5.2V, which is excellent for compensating for small transmission losses etc
* You can use the cheaper 500mA version [PowerBoost 500 Basic - 5V USB Boost ](https://www.adafruit.com/product/1903)

### Lithium Ion Battery Pack

[Lithium Ion Battery Pack - 3.7V 6600mAh](https://www.adafruit.com/product/353)

This battery is bigger than required, but was selected before I had power consumption figures.  Something around 2000mAh should be 
capable of covering several days of low solar availability.

## Power Consumption

To minimize power consumption, a number of steps where taken.

* The electronics where selected to consume as little as possible.  
    * The Raspberry Pi itself consumes around 125mA (0.625W)when idle
    * The DC/DC converted is around 90% efficient
* Minimum software load - Use something minimal, such as [Raspbian Stretch Lite](https://www.raspberrypi.org/downloads/raspbian/)
* Disable HDMI 
* Disable LED's (Software tweak on the Raspberry Pi, physical removal on the charger & DC/DC converter)
* Application software 'sleeps' between sensor readings
* Application does a back off if comm's are not available (Longer 'sleeps' between sending attempts)

An interesting article on Raspberry Pi Zero [power conservation](https://www.jeffgeerling.com/blogs/jeff-geerling/raspberry-pi-zero-conserve-energy)

## Other Items

The capacitor for the *Solar Lithium Ion/Polymer Charger* was increased as this is claimed to increase solar energy production (Not proven but cheap !)

The maximum charge rate was increased to the maximum (1000mA) available - Resistor swap. (See Adafruit documentation)

Temperature monitoring of the battery enabled via use of a termistor.  (See Adafruit documentation)

Accurate measurement of power consumption via USB was obtained using this very handy [device](https://www.tindie.com/products/mux/usb-31-type-a-power-meter-5-digit-precision/)

