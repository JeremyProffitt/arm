# Parts and purchasing

Planning allowance for the purchased items below: **US $778.78** before shipping and tax. Figures are budgeting allowances, not checked-out prices. Filament and any workshop tools are included only where explicitly listed. Reuse of existing supplies can change the total substantially.

Order the exact display and voltage variant specified. Generic fasteners, connector harnesses, relay contacts and wire must meet the listed dimensions and electrical ratings. Buy the servo horns and their screws with the servos; verify their actual thread and engagement before ordering extras.

## Controller, sensing, lights and power

| Ref / qty | Item | Required specification | Budget / each |
| --- | --- | --- | --- |
| E01 / 1 | [Raspberry Pi Raspberry Pi 4 Model B 4GB](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) | Master controller. 40-pin GPIO and four USB ports | $60.00 |
| E02 / 1 | [Raspberry Pi 15W USB-C Power Supply](https://www.raspberrypi.com/products/type-c-power-supply/) | Separate Pi supply. 5.1V 3A USB-C | $12.00 |
| E03 / 1 | Reputable flash vendor 32GB or larger microSD A1 | Operating system card. High endurance preferred | $12.00 |
| E04 / 1 | [Waveshare ESP32-S3-Touch-LCD-1.85 SKU28514](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.85) | Central face display. 55x55mm;360x360 ST77916 QSPI;USB-C;no B/C suffix | $35.00 |
| E05 / 5 | [Adafruit 3967 VL53L1X STEMMA QT](https://www.adafruit.com/product/3967) | Five interaction ranging sensors. 25.5x17.5x4.6mm;I2C0x29 | $14.95 |
| E06 / 1 | [Adafruit 5626 PCA9548 STEMMA QT](https://www.adafruit.com/product/5626) | Mux for five same-address sensors. TCA9548A-compatible;40.6x20.2x4.8mm;0x70 | $6.95 |
| E07 / 5 | [Adafruit STEMMA QT JST-SH4 cable](https://www.adafruit.com/category/619) | One separate cable per sensor. Length selected to assembled routing;100-300mm nominal | $2.00 |
| E08 / 1 | [Adafruit STEMMA QT to female header cable](https://www.adafruit.com/category/619) | Pi to mux upstream connector. 3.3V logic only | $2.00 |
| E09 / 4 | [Adafruit 1768 quarter NeoPixel60 ring](https://www.adafruit.com/product/1768) | Outer RGB emotion halo. 15RGB per quadrant;four form OD157.5mm ID144.8mm ring | $9.95 |
| E10 / 1 | [Adafruit 2862 NeoPixel24 RGBW natural white](https://www.adafruit.com/product/2862) | Inner white lamp ring. 24RGBW;OD65.5mm;only W channel used;4500K nominal | $24.95 |
| E11 / 1 | [Adafruit 1787 74AHCT125 DIP14](https://www.adafruit.com/product/1787) | Two data level shifters. 5V VCC;3.3V logic accepted;AHCT required | $1.50 |
| E12 / 2 | Generic 330ohm 0.25W resistor | LED input series resistors. One per independent data line | $0.10 |
| E13 / 2 | Generic 1000uF 10V electrolytic | LED ring supply reservoir. Observe polarity;one each ring | $1.00 |
| E14 / 1 | Generic 100nF ceramic | 74AHCT125 decoupling. Across DIP14 and DIP7 at socket | $0.10 |
| E15 / 1 | [Pololu D24V50F5 item2851](https://www.pololu.com/product/2851) | LED5V buck converter. 5V5A typical thermal-limited;17.8x20.3x8.8mm | $32.95 |
| E16 / 4 | [Waveshare ST3215 30kg.cm@12V](https://www.waveshare.com/product/modules/st3215-servo.htm) | Four joint bus servos. 12V version;4096ticks/rev;2.7A stall each;1Mbps default | $22.00 |
| E17 / 1 | [Waveshare Bus Servo Adapter A SKU25514](https://docs.waveshare.com/Bus_Servo_Adapter_A) | USB to TTL half-duplex bus adapter. ST selected;USB mode;separate low-current12V branch | $10.00 |
| E18 / 1 | [Mean Well GST220A12-R7B](https://www.meanwell.com/Upload/PDF/GST220A/GST220A-SPEC.PDF) | External enclosed motor/LED supply. 12V15A model;R7B powerDIN;keep outside printed enclosure | $95.00 |
| E19 / 1 | Generic Matching R7B powerDIN harness | DC supply breakout. Correct polarity;all specified parallel contacts;15A aggregate rated | $15.00 |
| E20 / 1 | Generic IEC C13 mains cord | External supply cord. Local approved cord;earth conductor intact | $7.00 |
| E21 / 1 | Generic Latching mushroom stop two NC contacts | Motor stop plus isolated Pi sense. NC1 interrupts12V relay coil;NC2 connects BCM27 to GND | $15.00 |
| E22 / 1 | Generic 12VDC coil relay with30A DC NO contact and socket | Hardware motor supply disconnect. Coil<=200mA;NO contacts>=15A at12VDC;socket16AWG | $12.00 |
| E23 / 1 | Generic 1N4007 diode | Relay coil flyback. Stripe/cathode to coil positive | $0.10 |
| E24 / 1 | Generic 15A DC fuse and holder | Main12V input branch. Holder and connector rated>=15A | $3.00 |
| E25 / 4 | Generic 3A time-delay DC fuse and holder | Individual servoV+ feeds. 18AWG star feeds;one fuse per servo | $3.00 |
| E26 / 1 | Generic 2A DC fuse and holder | Buck12V input branch. LED firmware capped20percent | $3.00 |
| E27 / 1 | Generic 1A DC fuse and holder | Bus adapter power branch. Do not run servo group current through adapter jack | $3.00 |
| E28 / 1 | Generic 0.5A DC fuse and holder | Relay coil branch. NC1 switches coil only | $3.00 |
| E29 / 1 | Generic 3A DC fuse and holder | 5V LED output branch. ProtectsLED18-22AWG harness | $3.00 |
| E30 / 1 | [Adafruit 3369 mini USB speaker](https://www.adafruit.com/product/3369) | Spoken Hi. USB audio;84x43x32mm;73.6g;keep volume modest | $12.50 |
| E31 / 1 | Generic USB-A to right-angle USB-C data cable | Pi to display. Flexible cable;strain relief;15mm rear plug envelope assumed | $7.00 |
| E32 / 1 | Generic USB data cable matching adapter | Pi to bus adapter. Use actual adapter USB connector type | $5.00 |
| E33 / 1 | Generic 16AWG /18AWG silicone wire and rated distribution terminals | Power harness. 16AWG trunk;18AWG motor branches;22AWGLED branches | $20.00 |
| E34 / 1 | Generic Small perfboard and DIP14 socket | Level shifter assembly. Insulate underside;strain relief all wires | $5.00 |
| E35 / 1 | Generic Pi4 heatsink and ventilation hardware | Thermal management. Check CPU temperature after assembled operation | $7.00 |
| E36 / 1 | Generic 10kohm resistor | External E-stop sense pullup. BCM27 to3.3V;open NC2 means asserted | $0.10 |

## Mechanical hardware and consumables

| Ref / qty | Item | Required specification | Budget / each |
| --- | --- | --- | --- |
| M01 / 1 | [Local metal supplier Custom ballast disc](https://www.onlinemetals.com/) | Steel ballast plate. Mild steel diameter180 thickness6 mm; 4 holes diameter4.4 at XY(+/-45,+/-35); 4 holes diameter3.4 at XY(+/-26,-36/-8); deburr; approx1.19kg | $25.00 |
| M02 / 1 | [Generic 6808-2RS](https://www.skf.com/group/products/rolling-bearings/ball-bearings/deep-groove-ball-bearings) | Yaw support bearing. 40mm bore x52mm OD x7mm width; sealed deep groove | $12.00 |
| M03 / 4 | Generic M4x25 | Base and tray bolts. M4 x25 socket head; steel plate6 + floor3 + spacer5 + tray3 | $0.25 |
| M04 / 4 | Generic M4x5 spacer | Tray standoffs. Metal spacer5mm length; 4.3mm bore; OD8 minimum | $0.40 |
| M05 / 4 | [Generic M4 nut]( ) | M4 lock nuts. ISO metric nyloc | $0.12 |
| M06 / 8 | [Generic M4 washer]( ) | M4 load spreading washers. OD12 minimum | $0.06 |
| M07 / 4 | Generic M3x16 | Yaw cradle through bolts. Through printed cradle3 steel6 and base3; nuts below base; tray has7mm head access | $0.16 |
| M08 / 2 | Generic M3x45 | Yaw rear body clamp bolts. Through bottom3 + body35 + keeper2.6; do not overtighten case | $0.30 |
| M09 / 2 | [Generic M3x50]( ) | Shoulder clamp bolts. Clamp through44mm tower width plus nuts | $0.30 |
| M10 / 4 | [Generic M3x16]( ) | Shoulder foot bolts. 6mm tower foot plus6mm platform plus nuts | $0.16 |
| M11 / 8 | Generic M3x60 | Arm rail cross bolts. 5+44+5mm stack plus nut; 4 per arm; include4 cassette ear positions | $0.40 |
| M12 / 24 | [Generic M3x10 nominal](https://www.waveshare.net/wiki/ST3215_Servo) | Pitch horn attachment screws. Nominal M3; 5mm rail +3.3mm spacer leaves1.7mm horn engagement; confirm vendor horn thread | $0.15 |
| M13 / 4 | [Generic M3x6 nominal](https://www.waveshare.net/wiki/ST3215_Servo) | Yaw horn attachment screws. 3mm web plus1mm washer leaves2mm engagement; confirm vendor horn thread | $0.15 |
| M14 / 6 | [Generic M3x12]( ) | Base lid screws. Into2.8mm plastic-thread-forming printed pilots | $0.15 |
| M15 / 4 | Generic M3x12 | Head yoke screws. 6mm fork mounting face +3mm shell floor; nuts on inside | $0.15 |
| M16 / 8 | Generic M3x10 | Outer bezel screws. 4mm bezel +1mm shim;2.8mm plastic-thread-forming pilot | $0.15 |
| M17 / 4 | Generic M3x12 | Central face screws. 4mm plate +1mm shim;2.8mm plastic-thread-forming pilot | $0.15 |
| M18 / 4 | Generic M3x10 | White ring carrier screws. 2mm carrier on dedicated radius45 bosses at z32.5 | $0.15 |
| M19 / 4 | Generic M3x25 | LCD cradle and retaining plate screws. 3mm retainer +15mm cradle; thread into head pillar at z14 | $0.20 |
| M20 / 16 | Generic M3x1 shim | Precision axial shims. M3 bore; thickness1mm; 12 underface/bezel plus4 yawhorn washers | $0.12 |
| M21 / 10 | [Generic M3x10]( ) | Sensor pod attachment bolts. 2 per pod through shell or frontplate | $0.15 |
| M22 / 10 | [Generic M2x14]( ) | Sensor edge frame screws. 2 per pod; pilot2.2 through holes; nuts | $0.15 |
| M23 / 10 | [Generic M2 nut]( ) | Sensor retainer nuts. ISO metric M2 | $0.08 |
| M24 / 30 | [Generic M3 nut]( ) | General M3 nuts. Include spare quantities for clamps sensorpods and platform | $0.10 |
| M25 / 50 | [Generic M3 washer]( ) | General M3 flat washers. Nominal0.5mm; not replacement for1mm axial shims | $0.05 |
| M26 / 4 | Generic M2.5x6 | Raspberry Pi fasteners. Pi4 four mounting holes; printed standoffs may be tappedM2.5 | $0.12 |
| M27 / 4 | Generic Rubber feet | Adhesive anti slip feet. 20mm diameter x5mm high minimum; place radius90 | $0.40 |
| M28 / 1 | Generic Translucent PETG | Frosted optical printing filament. Natural/translucent; approximately60g including trials; solid1.2mm optical skin | $20.00 |
| M29 / 1 | Generic PETG | Structural filament. Approx1kg roll; actual slicer mass varies;6 walls on arm rails | $22.00 |
| M30 / 1 | Generic Neutral cure silicone | Small adhesive tube. 3 small removable dots for inner diffuser and edgefoam; electronics compatible | $6.00 |
| M31 / 1 | Generic Thin PCB foam | Closed cell foam tape. 0.5 and1mm thickness; LCD edge preload only | $4.00 |
| M32 / 1 | [Generic LED retaining tape]( ) | Electronics compatible thin adhesive strips. Attach LED ring PCB on support posts without covering LED optics | $3.00 |
| M33 / 1 | Generic Desk clamp | Optional commercial padded desk clamp. Use only if assembly reach/mass exceeds validated stable envelope; not a printed load bearing clamp | $12.00 |
| M34 / 12 | [Generic M2.5x12]( ) | Optional harness clip screws. For6 printed cable saddles; use selftapped pilots or cableties | $0.12 |
| M35 / 10 | Generic Soft closed-cell foam strip | Required ToF edge preload strips. 18x2x6mm each; compress gently to5.4mm between PCB edge and retaining frame;2 per sensor | $0.20 |

## Printable part schedule

27 unique STL files; 52 printed pieces including the fit coupon and optional cable clips. Quantities control the print run. The drawing index uses the same part order.

| Drawing / qty | STL identifier | Material / print orientation |
| --- | --- | --- |
| P01 / 1 | `base_tub` | PETG; floor down |
| P02 / 1 | `base_lid` | PETG; flat annulus down |
| P03 / 1 | `electronics_tray` | PETG; plate down |
| P04 / 1 | `yaw_mount` | PETG; base down |
| P05 / 1 | `yaw_cap` | PETG; flat down |
| P06 / 1 | `turntable` | PETG; neck down |
| P07 / 1 | `shoulder_tower` | PETG; foot down |
| P08 / 1 | `shoulder_cap` | PETG; flat down |
| P09 / 2 | `upper_rail` | PETG; broad face down |
| P10 / 2 | `forearm_rail` | PETG; broad face down |
| P11 / 2 | `servo_cassette` | PETG; closed side down |
| P12 / 2 | `cassette_cap` | PETG; flat down |
| P13 / 4 | `cross_spacer` | PETG; cylinder upright |
| P14 / 6 | `horn_spacer` | PETG; flat down |
| P15 / 1 | `head_yoke` | PETG; rear mounting plate on bed; rotate180X |
| P16 / 1 | `head_shell` | PETG; rear disc down |
| P17 / 1 | `outer_bezel` | PETG; front lip down |
| P18 / 1 | `face_center` | black PETG; flat front down |
| P19 / 1 | `white_carrier` | PETG; flat down |
| P20 / 1 | `lcd_cradle` | PETG; flat base down |
| P21 / 1 | `lcd_retainer` | black PETG; flat down |
| P22 / 1 | `outer_diffuser` | natural/translucent PETG; smooth optical face on bed |
| P23 / 1 | `inner_diffuser` | natural/translucent PETG; smooth optical face on bed |
| P24 / 5 | `sensor_pod` | PETG; rear flange down |
| P25 / 5 | `sensor_retainer` | PETG; flat down |
| P26 / 6 | `cable_clip` | PETG; flat down |
| P27 / 1 | `fit_coupon` | PETG; flat down |
