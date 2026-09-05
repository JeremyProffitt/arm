// LUMA face coprocessor. Exact board: Waveshare ESP32-S3-Touch-LCD-1.85,
// SKU28514, no B/C suffix. The Pi4 controls all behaviors over USB serial.
#include <Arduino.h>
#include <Wire.h>
#include <Arduino_GFX_Library.h>
#include <math.h>
#include <driver/spi_master.h>
#include "panel_init.h"

Arduino_DataBus *bus = nullptr;
Arduino_GFX *lcd = nullptr;
Arduino_Canvas *face = nullptr;
String expression = "idle";
uint32_t expressionStart = 0, lastHost = 0, lastFrame = 0;
char input[64];
size_t inputLength = 0;
bool overflow = false;

bool expanderWrite(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(0x20);
  Wire.write(reg); Wire.write(value);
  return Wire.endTransmission() == 0;
}

int panelVariant() {
  // Read ID at the vendor's conservative5MHz before Arduino_GFX takes the bus.
  // Commands are32bits, opcode0x0B / register0x04 / trailing dummy byte.
  spi_bus_config_t cfg = {};
  cfg.mosi_io_num=46; cfg.miso_io_num=45; cfg.sclk_io_num=40;
  cfg.quadwp_io_num=42; cfg.quadhd_io_num=41;
  cfg.data4_io_num=-1; cfg.data5_io_num=-1; cfg.data6_io_num=-1; cfg.data7_io_num=-1;
  cfg.max_transfer_sz=64;
  if (spi_bus_initialize(SPI2_HOST,&cfg,SPI_DMA_CH_AUTO)!=ESP_OK) return -1;
  spi_device_interface_config_t dev = {};
  dev.command_bits=8; dev.address_bits=24;
  dev.clock_speed_hz=5000000; dev.spics_io_num=21;
  dev.flags=SPI_DEVICE_HALFDUPLEX; dev.queue_size=1;
  spi_device_handle_t handle;
  if (spi_bus_add_device(SPI2_HOST,&dev,&handle)!=ESP_OK) {
    spi_bus_free(SPI2_HOST); return -1;
  }
  spi_transaction_t transaction = {};
  transaction.cmd=0x0B; transaction.addr=0x000400; transaction.rxlength=32;
  transaction.flags=SPI_TRANS_USE_RXDATA;
  esp_err_t status=spi_device_polling_transmit(handle,&transaction);
  uint8_t *id=transaction.rx_data;
  Serial.printf("PANEL %02X %02X %02X %02X\n",id[0],id[1],id[2],id[3]);
  int variant = -1;
  if(status==ESP_OK && id[0]==0 && id[2]==0x7F && id[3]==0x7F) {
    if(id[1]==0x7F) variant=0;
    if(id[1]==0x02) variant=1;
  }
  spi_bus_remove_device(handle);
  spi_bus_free(SPI2_HOST);
  return variant;
}

void acceptLine() {
  input[inputLength] = 0;
  if (strcmp(input, "PING") == 0) {
    lastHost = millis(); Serial.println("PONG"); return;
  }
  if (strncmp(input, "FACE ", 5) == 0) {
    String next = String(input + 5);
    if (next == "idle" || next == "wink" || next == "hi" || next == "happy" || next == "fault") {
      if (next != expression) { expression = next; expressionStart = millis(); }
      lastHost = millis(); Serial.print("OK "); Serial.println(expression); return;
    }
  }
  Serial.println("ERR command");
}

void readHost() {
  while (Serial.available()) {
    char ch = static_cast<char>(Serial.read());
    if (ch == '\r') continue;
    if (ch == '\n') {
      if (!overflow) acceptLine(); else Serial.println("ERR length");
      inputLength = 0; overflow = false;
    } else if (inputLength < sizeof(input)-1) {
      input[inputLength++] = ch;
    } else {
      overflow = true;
    }
  }
}

void strokeArc(int cx, int cy, int rx, int ry, float start, float end, int width, uint16_t color) {
  for (float a=start; a<=end; a+=0.03f)
    face->fillCircle(cx+rx*cosf(a), cy+ry*sinf(a), width, color);
}

void paint() {
  const uint16_t black = 0x0000, cyan = 0x67DF, blush = 0xC1EF;
  float t = (millis()-expressionStart)/1000.f;
  bool offline = millis()-lastHost>1500;
  face->fillScreen(black);
  uint16_t color = (expression == "fault" || offline) ? 0xFC60 : cyan;
  if (expression == "fault" || offline) {
    face->fillRoundRect(90,136,60,12,6,color);
    face->fillRoundRect(210,136,60,12,6,color);
    face->fillRoundRect(150,235,60,9,4,color);
    face->setTextColor(color); face->setTextSize(2); face->setCursor(120,285);
    face->print(offline ? "WAITING" : "PAUSED");
  } else {
    bool wink = expression=="wink" && fmodf(t,3.f)>0.65f && fmodf(t,3.f)<1.45f;
    bool blink = expression=="idle" && (millis()%5200)>5050;
    bool happy = expression=="happy";
    if (happy) {
      strokeArc(119,155,32,22,3.25,6.15,6,color);
      strokeArc(241,155,32,22,3.25,6.15,6,color);
    } else {
      if (blink) face->fillRoundRect(92,146,54,10,5,color);
      else face->fillRoundRect(95,107,48,74,22,color);
      if (wink || blink) face->fillRoundRect(214,146,54,10,5,color);
      else face->fillRoundRect(217,107,48,74,22,color);
    }
    face->fillCircle(77,207,13,blush); face->fillCircle(283,207,13,blush);
    if (expression=="hi") {
      int opening = 8 + int(12*(0.5f+0.5f*sinf(t*12)));
      face->fillCircle(180,232,opening,color);
      face->setTextColor(color); face->setTextSize(3); face->setCursor(155,289); face->print("Hi!");
    } else {
      strokeArc(180,205,51,happy?45:30,0.15,2.99,6,color);
    }
  }
  face->flush();
}

void setup() {
  Serial.begin(115200);
  Wire.begin(11,10);
  Wire.setClock(100000);
  // TCA9554 EXIO1=P0 touch reset, EXIO2=P1 LCD reset, EXIO3=P2 SD CS.
  // Leave EXIO4..8 as inputs and deselect unused SD.
  expanderWrite(1,0x07);
  if (!expanderWrite(3,0xF8)) {
    Serial.println("ERR expander");
    while (true) delay(100);
  }
  expanderWrite(1,0x05); delay(120);
  expanderWrite(1,0x07); delay(120);
  int variant=panelVariant();
  if(variant<0) {
    Serial.println("ERR unknown panel ID");
    while(true) delay(100);
  }
  bus = new Arduino_ESP32QSPI(21,40,46,45,42,41);
  const uint8_t *init = variant ? luma_panel_new : luma_panel_old;
  size_t initSize = variant ? sizeof(luma_panel_new) : sizeof(luma_panel_old);
  lcd = new Arduino_ST77916(bus,GFX_NOT_DEFINED,0,true,360,360,0,0,0,0,init,initSize);
  face = new Arduino_Canvas(360,360,lcd);
  pinMode(5,OUTPUT); digitalWrite(5,HIGH);
  if (!face->begin()) {
    Serial.println("ERR display");
    while (true) delay(100);
  }
  lastHost=millis();
  Serial.println("READY LUMA1");
}

void loop() {
  readHost();
  if (millis()-lastFrame >= 40) { lastFrame=millis(); paint(); }
  delay(1);
}
