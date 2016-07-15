# kiva-raspi
RaspberryPi powered map that lights up in real time with loans

## Setup

Put the pins in:
North America
South America
Africa
Middle East
South Asia

Use a common ground.

Pin locations: https://www.google.com/search?q=pin+17+raspi+b&espv=2&biw=1436&bih=702&source=lnms&tbm=isch&sa=X&ved=0ahUKEwj68oTq47_NAhUC7GMKHcIMB5IQ_AUIBigB#imgrc=oSXvaM-s5hJm8M%3A

## Example command to run it on startup:
Edit ```/etc/rc.local```
(You can change it to accept bash commands (like pushd and popd) by changing the first line to ```#!/bin/bash```

```
#!/bin/bash

# Go to directory with your code and save current directory onto the stack
pushd /home/pi/kiva-raspi/      
# Runs python command put the output and error output into dev/null (no where) and create a seperate thread so it’s not blocking.
python main.py > /dev/null 2>&1 &
# return to previous pushed directory
popd   
exit 0
```
