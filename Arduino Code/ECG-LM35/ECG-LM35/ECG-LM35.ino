const int ECG_PIN = A0;
const int TEMP_PIN = A1;
const int ECG_SAMPLES = 30;
int ecgBuffer[ECG_SAMPLES];
int ecgIndex = 0;

unsigned long lastECGPrint = 0;
unsigned long lastECGRead = 0;
unsigned long lastTempMillis = 0;
unsigned long lastTempPrintMillis = 0;

const unsigned long ECG_INTERVAL = 20;              // 50 Hz for smoother graph
const unsigned long ECG_AVG_PRINT_INTERVAL = 1000;  // Upload ECG once per second
const unsigned long TEMP_SAMPLE_INTERVAL = 1000;
const unsigned long TEMP_AVG_INTERVAL = 10000;

float tempSum = 0;
int tempCount = 0;

const int LO_PLUS = 10;
const int LO_MINUS = 11;

void setup() {
  Serial.begin(9600);
  pinMode(LO_PLUS, INPUT);
  pinMode(LO_MINUS, INPUT);
}

void loop() {
  unsigned long now = millis();

  // --- ECG Sampling ---
  if (now - lastECGRead >= ECG_INTERVAL) {
    lastECGRead = now;

    if (digitalRead(LO_PLUS) == 1 || digitalRead(LO_MINUS) == 1) {
      Serial.println("{\"status\":\"Lead off detected\"}");
    } else {
      int raw = analogRead(ECG_PIN);
      ecgBuffer[ecgIndex] = raw;
      ecgIndex = (ecgIndex + 1) % ECG_SAMPLES;
    }
  }

  // --- ECG Upload Every 1 Second (Average of 30 samples) ---
  if (now - lastECGPrint >= ECG_AVG_PRINT_INTERVAL) {
    lastECGPrint = now;

    int validCount = 0;
    long sum = 0;

    for (int i = 0; i < ECG_SAMPLES; i++) {
      if (ecgBuffer[i] >= 300 && ecgBuffer[i] <= 800) {
        sum += ecgBuffer[i];
        validCount++;
      }
    }

    if (validCount > 0) {
      int avg = sum / validCount;
      Serial.print("{\"ecg\":");
      Serial.print(avg);
      Serial.println("}");
    }
  }

  // --- TEMP Sampling ---
  if (now - lastTempMillis >= TEMP_SAMPLE_INTERVAL) {
    lastTempMillis = now;

    int adc = analogRead(TEMP_PIN);
    float voltage = adc * 5.0 / 1023.0;
    float temp = voltage * 100;

    if (temp >= 34 && temp <= 39) {
      tempSum += temp;
      tempCount++;
    }
  }

  // --- TEMP Average Report ---
  if (now - lastTempPrintMillis >= TEMP_AVG_INTERVAL) {
    lastTempPrintMillis = now;

    if (tempCount > 0) {
      float avg = tempSum / tempCount;
      Serial.print("{\"temperature\":");
      Serial.print(avg, 2);
      Serial.println("}");
    } else {
      Serial.println("{\"temperature\":\"No valid readings\"}");
    }

    tempSum = 0;
    tempCount = 0;
  }
}