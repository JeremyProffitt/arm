The graphics library is Arduino_GFX v1.6.5 by Moon On Our Nation and its contributors, obtained through PlatformIO under its own license:
https://github.com/moononournation/Arduino_GFX/tree/v1.6.5

`src/panel_init.h` contains hardware register data converted to the Arduino_GFX operation format from the Waveshare ESP32-S3-Touch-LCD-1.85 reference demo (archive published2025-04-18). Default table original copyright2023 Espressif Systems (Shanghai) CO LTD, Apache-2.0. The board vendor's revised table is in `Arduino/examples/LVGL_Arduino/Display_ST77916.cpp`; the original default is in `esp_lcd_st77916.c`. Command values, data byte order and waits were retained; RGB565 format is explicitly set at the end.

Source archive:
https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.85/ESP32-S3-Touch-LCD-1.85-Demo.zip

Apache2.0 license text:
https://www.apache.org/licenses/LICENSE-2.0.txt

No audio recordings, vendor speech models, or example applications are redistributed in the project deliverable.
