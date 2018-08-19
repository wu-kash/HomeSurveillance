# HomeSurveillance
A user interface that displays the state of lights/doors/windows in a home. Each door/window/light is connected to a sensor that is hooked up to the Raspberry PI. Where a high logic level will result in the object being activated and a low logic level will deactivate the object. The home layout can be modified and saved for future use and the object data is stored in Objects.txt

The logs of the object activities are stored in LOGS.txt, which records the time, date and state of each object that is interacted with.

Used with a Raspberry PI B+ v1.2 primarily, however can be modified to work with other models aswell. The gpio_list has to be modified to support other models.
