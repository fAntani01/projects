#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "esp_bt_device.h"

// UUID per servizio e caratteristica
#define SERVICE_UUID        "12345678-1234-5678-1234-56789abcdef0"
#define CHARACTERISTIC_UUID "abcdef01-1234-5678-1234-56789abcdef0"

BLEServer* pServer = nullptr;
BLECharacteristic* pCharacteristic = nullptr;
bool deviceConnected = false;

// Contatore opzionale
uint32_t counter = 0;

// Array dei pin dei pulsanti
const int buttonPins[8] = {2, 4, 16, 17, 18, 19, 21, 22};
// Array dello stato precedente dei pulsanti
bool buttonState[8] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};

// Callback connessione/disconnessione
class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) override {
    deviceConnected = true;
    Serial.println("Dispositivo connesso");
  }

  void onDisconnect(BLEServer* pServer) override {
    deviceConnected = false;
    Serial.println("Dispositivo disconnesso");
    pServer->startAdvertising();
  }
};

void printDeviceAddress() {
  const uint8_t* point = esp_bt_dev_get_address();
  for (int i = 0; i < 6; i++) {
    char str[3];
    sprintf(str, "%02X", (int)point[i]);
    Serial.print(str);
    if (i < 5) Serial.print(":");
  }
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Avvio BLE ESP32...");
 

  // Inizializza BLE
  BLEDevice::init("ESP32_BLE_Server");

  // Stampa MAC BLE
  printDeviceAddress();

  // Crea server BLE
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Servizio e caratteristica
  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );
  pCharacteristic->addDescriptor(new BLE2902());
  pService->start();

  // Advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  BLEDevice::startAdvertising();

  Serial.println("BLE pronto e in advertising");

  // Configura pin dei pulsanti come input pull-up
  for (int i = 0; i < 8; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
}

void loop() {
  if (deviceConnected) {
    // Controllo pulsanti
    for (int i = 0; i < 8; i++) {
      bool currentState = digitalRead(buttonPins[i]);

            // Se il pulsante è premuto (LOW) e prima era HIGH -> invia codice
      if (currentState == LOW && buttonState[i] == HIGH) {
        char msg[10];
        snprintf(msg, sizeof(msg), "BTN%d", i+1);
        pCharacteristic->setValue((uint8_t*)msg, strlen(msg));
        pCharacteristic->notify();
        Serial.print("Inviato: ");
        Serial.println(msg);
      }
      buttonState[i] = currentState; // aggiorna stato precedente
    }
  }

  delay(50); // piccolo debounce software
}
