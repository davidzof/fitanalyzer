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
zones = [(148, "LT1", "green"),(162, "LT2", "red"),(None, "LT3","")]
## 5 zone model
#zones = [(112, "Zone 1", "green"),(130, "Zone 2", "yellow"),(148, "Zone 3", "orange"),(167, "Zone 4", "red"),(None, "Zone 5","")]

```
## DFA Alpha1
This is supposed to predict Lactate 1 and 2 thresholds. In the image below LT1 occurs at DFA 0.75 and is 149bpm and LT2 at DFA 0.5 and is 162 bpm. This chart is from a 4 hour mixed ride: flats, long climbs, short climbs

![DFA Alpha1](https://github.com/davidzof/fitanalyzer/blob/main/docs/dfa-alpha1.png)

## Zones
Fitanalyzer can show both Time in Zone (TIZ) and Session Goal / Time in Zone (SG/TIG). SG/TIZ cleans up very small intervals, say where you were aiming for a Zone3 Interval but had to slow down for lights and dropped briefly into Zone2. The 3 segments will be combined into a single Z3 segment. It gives a more realistic idea of the training session.

TIZ

![Time in Zone]((https://github.com/davidzof/fitanalyzer/blob/main/docs/4x8s.png)




## TO DO
* Make spike filter configurable
* Make it easier to add new graph types: restructure code
* Add actual time in each zone to zone graphs
* Add gpx files
* Add altitude graph as second plot - DONE
* Add mapping?
* Add altitude calculations to file
* Save as GPX?
