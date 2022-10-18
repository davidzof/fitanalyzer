# fitanalyzer
Python GUI program for visualizing FIT data files

## Currently you can visualize
1. Heart Rate data
2. Heart Rate and Power data
3. DFA Alpha 1 (Heart Rate Variablity)
4. Heart Rate vs DFA Alpha 1 with trend line

## Properties file

The properties file: properties.ini located in the home directory enables you to
configure some personal details.

First of all set your min and max heart rate. These are used to filter spikes. Any
values outside these parameters

You can also configure your HR zones depending on the model you are using.
Zones are python arrays of tuples. A tuple is a collection of values,
in this case a max HR for the zone, a name and a color code.
```editorconfig
[DEFAULT]
minhr = 51
maxhr = 185
spikes = 0.5

[HEARTRATE_ZONES]
#zones = [(148, "LT1", "green"),(162, "LT2", "red"),(None, "LT3","")]
## 5 zone model
#zones = [(137, "Zone 1", "green"),(150, "Zone 2", "yellow"),(163, "Zone 3", "orange"),(174, "Zone 4", "red"),(None, "Zone 5","")]
```

## TO DO
* Add altitude plot to HR screen
* Make spike filter configurable
* Add gpx files
* Add altitude graph as second plot
* Add mapping?
* Add altitude calculations to file
* Save as GPX?