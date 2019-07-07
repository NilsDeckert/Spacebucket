#include "../rc-switch/RCSwitch.h"
#include <stdlib.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    int PIN = 0;                            // wiring Pi layout
    int codeSocketDon = 1049937;            // code to turn socket on
    int codeSocketDoff = 1049940;           // code to turn socket off

    if (wiringPiSetup() == -1) return 1;

    RCSwitch mySwitch = RCSwitch();
    mySwitch.enableTransmit(PIN);

    if (atoi(argv[1]) == 1) {               // if program is startet with argument '1'
        mySwitch.send(codeSocketDon, 24);
    } else {
        mySwitch.send(codeSocketDoff, 24);
    }
    return 0;
}

// Source: https://tutorials-raspberrypi.de/raspberry-pi-funksteckdosen-433-mhz-steuern/
