# Point-to-point wiring schedule

Use these connection names together with the electrical chapter. Physical Raspberry Pi header numbers and BCM GPIO numbers are explicitly distinguished. Disconnect the supplies while changing wiring. Nets starting with `DSI_` apply only to the optional 4-inch DSI head and replace `FACE_USB`.

| Net | From → to | Cable / connection detail |
| --- | --- | --- |
| 3V3_LOGIC | Raspberry Pi4: physical1 3V3 → Mux5626: VIN | STEMMAQT upstream red. All I2C pullups stay3.3V |
| GND_LOGIC | Raspberry Pi4: physical6 GND → Mux5626: GND | STEMMAQT upstream black. Connect DCSTARground also |
| I2C_SDA | Raspberry Pi4: physical3 BCM2 → Mux5626: SDA | STEMMAQT upstream blue. I2C bus1 at100kHz |
| I2C_SCL | Raspberry Pi4: physical5 BCM3 → Mux5626: SCL | STEMMAQT upstream yellow. I2C bus1 at100kHz |
| TOF_FRONT | Mux5626: port0 → VL53L1X front pedestal: STEMMAQT4pin | 4conductor JSTSH. Address0x29 isolated on channel0; wall angle90deg |
| TOF_FRONT_LEFT | Mux5626: port1 → VL53L1X front-left pedestal: STEMMAQT4pin | 4conductor JSTSH. Wall angle162deg |
| TOF_REAR_LEFT | Mux5626: port2 → VL53L1X rear-left pedestal: STEMMAQT4pin | 4conductor JSTSH. Wall angle234deg |
| TOF_REAR_RIGHT | Mux5626: port3 → VL53L1X rear-right pedestal: STEMMAQT4pin | 4conductor JSTSH. Wall angle306deg |
| TOF_FRONT_RIGHT | Mux5626: port4 → VL53L1X front-right pedestal: STEMMAQT4pin | 4conductor JSTSH. Wall angle18deg; leave every optical aperture clear |
| PWM_VCC | Raspberry Pi4: physical1 3V3 → PCA9685: VCC | 22AWG. Powers controller logic only; never powers a servo |
| PWM_GROUND | DCstar: GND → PCA9685: GND | 18AWG. Common reference to Pi sensor bus and all servo signal returns |
| PWM_SDA | Raspberry Pi4: physical3 BCM2 → PCA9685: SDA | 26AWG. Shared upstream I2C bus; address0x40 |
| PWM_SCL | Raspberry Pi4: physical5 BCM3 → PCA9685: SCL | 26AWG. Shared upstream I2C bus;50Hz PWM configured in software |
| PWM_ENABLE | DCstar: GND → PCA9685: /OE | 26AWG. Active-low output enable held low |
| RGB_DATA3V3 | Raspberry Pi4: physical19 BCM10 MOSI → 74AHCT125: DIP2 1A | 26AWG. Do not connect SPI clock to ring |
| RGB_DATA5V | 74AHCT125: DIP3 1Y → RGB ring quadrant1: DIN via330ohm | 26AWG. Resistor at first ring input |
| RGB_CHAIN1 | RGB quadrant1: DOUT → RGB quadrant2: DIN | solder jumper. Connect common5V andGND at all quadrants |
| RGB_CHAIN2 | RGB quadrant2: DOUT → RGB quadrant3: DIN | solder jumper. Mechanical backing supports solder joints |
| RGB_CHAIN3 | RGB quadrant3: DOUT → RGB quadrant4: DIN | solder jumper. Do not connect lastDOUT back to firstDIN |
| WHITE_DATA3V3 | Raspberry Pi4: physical12 BCM18 PWM0 → 74AHCT125: DIP5 2A | 26AWG. Disable onboard analog audio |
| WHITE_DATA5V | 74AHCT125: DIP6 2Y → 24RGBW inner ring: DIN via330ohm | 26AWG. SeparateGRBW data stream |
| SHIFT_ENABLE | DCstar: GND → 74AHCT125: DIP1 /1OE andDIP4 /2OE | 26AWG. Active outputs; tie both low |
| SHIFT_UNUSED | 5VLED: +5V → 74AHCT125: DIP10 /3OE andDIP13 /4OE | 26AWG. Unused outputs disabled |
| SHIFT_UNUSED_INPUT | DCstar: GND → 74AHCT125: DIP9 3A andDIP12 4A | 26AWG. UnusedDIP8 andDIP11 outputs unconnected |
| SHIFT_SUPPLY | 5VLED: +5V → 74AHCT125: DIP14 VCC | 24AWG. 100nF betweenDIP14 andDIP7 |
| SHIFT_GROUND | DCstar: GND → 74AHCT125: DIP7 GND | 24AWG. Shared reference toPi andboth rings |
| PI_GROUND | Raspberry Pi4: physical9 GND → DCstar: GND | 22AWG. Common ground only; never tie5VLED toPi5V |
| PI_POWER | Pi official supply: USB-C5.1V3A → Raspberry Pi4: USB-Cpower | factory cable. Independent from motor12V |
| FACE_USB | Raspberry Pi4: USB-Aport1 → DisplaySKU28514: USB-C | data cable. Do not add a second5V power feed |
| AUDIO_USB | Raspberry Pi4: USB-Aport3 → USB speaker3369: USB | captive cable. LimitUSB total current toPi specification |
| DC_INPUT | MeanWellGST220A12: R7B+12V → Main15Afuse: input | 16AWG. Use correctparallel contacts from supply drawing |
| DC_MAIN | Main15Afuse: output → DC12Vdistribution: +12V | 16AWG. Supply remains outside printed enclosure |
| DC_RETURN | MeanWellGST220A12: R7Breturn → DCstar: GND | 16AWG. All high-current returns star here |
| STOP_COIL_FEED | DC12Vdistribution: +12V → 0.5Afuse: input | 22AWG. Coil branch |
| STOP_NC1 | 0.5Afuse: output → StopNC1: COM | 22AWG. NoPiGPIO in this branch |
| STOP_COIL_PLUS | StopNC1: NC → Relay: coilpositive | 22AWG. Diodecathode stripe here |
| STOP_COIL_MINUS | Relay: coilnegative → DCstar: GND | 22AWG. Diodeanode here |
| MOTOR_RELAY_IN | DC12Vdistribution: +12V → Relay: COM highcurrent | 16AWG. NOcontact>=15A12VDC |
| MOTOR_RELAY_OUT | Relay: NO highcurrent → Servo regulator7.5Afuse: input | 16AWG. Stop removes regulator input and all motor V+ independent of software |
| SERVO_REG_INPUT | Servo regulator7.5Afuse: output → PololuD42V110F6: VIN | 16AWG. 12V nominal input; mount with airflow |
| SERVO_6V | PololuD42V110F6: VOUT6V → Servo4way fusedstar: input | 16AWG. Verify6V and polarity before connecting any servo |
| SERVO_BULK | Servo6Vstar: +6V/GND → 2200uF10Vcapacitor: +/- | short18AWG. Observe polarity and place near star distribution |
| SERVO_POWER1 | Servo3Afuse1: output → YawDS3218MG: V+ | 18AWG. Separate6V feed; do not carry power through PCA9685 traces |
| SERVO_POWER2 | Servo3Afuse2: output → ShoulderDS3218MG: V+ | 18AWG. Separate6V feed |
| SERVO_POWER3 | Servo3Afuse3: output → ElbowDS3218MG: V+ | 18AWG. Separate6V feed |
| SERVO_POWER4 | Servo3Afuse4: output → WristDS3218MG: V+ | 18AWG. Separate6V feed |
| SERVO_GROUNDS | AllfourDS3218MG: GND → DCstar: GND | 18AWG. One power return per servo; common with PCA9685 logic ground |
| SERVO_PWM1 | PCA9685: channel0 signal → YawDS3218MG: PWM | 26AWG. 500-2500us range;1500us nominal neutral; signal and ground only at controller |
| SERVO_PWM2 | PCA9685: channel1 signal → ShoulderDS3218MG: PWM | 26AWG. Confirm direction before fitting loaded horn |
| SERVO_PWM3 | PCA9685: channel2 signal → ElbowDS3218MG: PWM | 26AWG. Confirm direction before fitting loaded horn |
| SERVO_PWM4 | PCA9685: channel3 signal → WristDS3218MG: PWM | 26AWG. Confirm direction before fitting loaded horn |
| STOP_SENSE | Raspberry Pi4: physical13 BCM27 → StopNC2: COM | 26AWG. External10kohm toPi3.3V |
| STOP_SENSE_RETURN | StopNC2: NC → Raspberry Pi4: physical14 GND | 26AWG. Opencontact orbrokenwire readsstop |
| BUCK_INPUT | DC12Vdistribution: +12V via2Afuse → PololuD24V50F5: VIN | 22AWG. ENleftunconnected |
| BUCK_GND | PololuD24V50F5: GND → DCstar: GND | 22AWG. Shortreturn |
| LED_FUSED | PololuD24V50F5: VOUT5V → 3Afuse: input | 22AWG. Verify5VbeforeconnectingLEDs |
| LED_RGB_POWER | 3Afuse: output5V → Outer60RGB: 5V atoppositequadrants | 22AWG. 1000uF10Vcap at ring |
| LED_WHITE_POWER | 3Afuse: output5V → Inner24RGBW: 5V | 22AWG. 1000uF10Vcap at ring |
| LED_RETURNS | Bothrings: GND → DCstar: GND | 22AWG. KeepLEDreturnseparatefromI2Creturnuntilstar |
| DSI_DATA | Raspberry Pi4: DSI connector → 4inch DSI LCD (C): 15-pin DSI FPC | 15-pin1.0mm FFC800mm type A. Optional head only;replaces FACE_USB;route through both arm cable ports with a service loop at each joint |
| DSI_POWER | Raspberry Pi4: physical4 5V → 4inch DSI LCD (C): HP2.0 4-pin 5V | 22AWG. Optional head only;display draws from the Pi supply in place of the USB display |
| DSI_GROUND | Raspberry Pi4: physical39 GND → 4inch DSI LCD (C): HP2.0 4-pin GND | 22AWG. Optional head only;SDA and SCL contacts of this plug stay empty;touch and backlight use the DSI connector I2C bus10 |
