const int PULSE_SENSOR_PIN = A0;  // Analog input pin for pulse sensor

// Signal smoothing and buffer setup
int Signal = 0;
int SmoothedSignal = 0;
int SignalBuffer[20];  // Increased buffer size for better smoothing
int SignalIndex = 0;

// Beat detection
bool BeatDetected = false;
unsigned long LastBeatTime = 0;
unsigned long BeatInterval = 0;
int HeartRate = 0;
int LastHeartRate = 0;

// Normalization parameters
int MinSignal = 1023;  // Initial max signal
int MaxSignal = 0;     // Initial min signal
int NormalizedSignal = 0;
const int MinNormalizationRange = 20;  // Minimum difference to avoid flat range

unsigned long StabilizationStart = 0;
const long StabilizationDelay = 2000;  // Stabilization time before detecting heart rate

unsigned long LastPrintTime = 0;
const long PrintInterval = 1000;  // 1-second print interval

// Declare the missing variable LastNormalized
int LastNormalized = 0;  // Initialize LastNormalized to 0

void setup() {
  Serial.begin(9600);  // Initialize serial communication
  pinMode(LED_BUILTIN, OUTPUT);  // Pin for the LED (used to blink on beat)

  // Initialize the signal buffer to zero
  for (int i = 0; i < 20; i++) SignalBuffer[i] = 0;  // Increased buffer size
}

void loop() {
  // 1. Read the signal from the pulse sensor
  Signal = analogRead(PULSE_SENSOR_PIN);

  // Add the new signal value to the buffer and compute the smoothed signal
  SignalBuffer[SignalIndex] = Signal;
  SignalIndex = (SignalIndex + 1) % 20;  // Update buffer index

  SmoothedSignal = 0;
  for (int i = 0; i < 20; i++) {
    SmoothedSignal += SignalBuffer[i];
  }
  SmoothedSignal /= 20;  // Average the last 20 signal readings

  // 2. Calculate signal variance for finger detection
  int variance = getSignalVariance();

  // 3. Finger detection logic (loosen the threshold for testing)
  bool fingerDetected = SmoothedSignal > 200 && variance > 10;  // Adjusted threshold

  // Print smoothed signal and variance for debugging
  Serial.print("Smoothed Signal: ");
  Serial.print(SmoothedSignal);
  Serial.print("  Variance: ");
  Serial.println(variance);

  // If no finger is detected, print message and skip to next loop iteration
  if (!fingerDetected) {
    HeartRate = 0;
    BeatDetected = false;
    digitalWrite(LED_BUILTIN, LOW);  // Turn off LED when no pulse is detected
    if (millis() - LastPrintTime >= PrintInterval) {
      LastPrintTime = millis();
      Serial.println("No finger detected.");
    }
    delay(50);  // Short delay before checking again
    return;
  }

  // 4. Handle stabilization period
  if (StabilizationStart == 0) {
    StabilizationStart = millis();  // Start stabilization timer
  }

  if (millis() - StabilizationStart < StabilizationDelay) {
    // During stabilization, don't calculate heart rate yet
    Serial.println("Waiting for stabilization...");
    return;
  }

  // 5. Track the min/max signal and normalize the signal value
  if (SmoothedSignal < MinSignal) MinSignal = SmoothedSignal;
  if (SmoothedSignal > MaxSignal) MaxSignal = SmoothedSignal;

  // Ensure that there is a sufficient gap between min and max to prevent squashing
  if (MaxSignal - MinSignal < MinNormalizationRange) {
    MaxSignal = MinSignal + MinNormalizationRange;
  }

  // Normalize the signal to a range of 0 to 100
  NormalizedSignal = map(SmoothedSignal, MinSignal, MaxSignal, 0, 100);
  NormalizedSignal = constrain(NormalizedSignal, 0, 100);

  // Print normalized signal for debugging
  Serial.print("Normalized Signal: ");
  Serial.println(NormalizedSignal);

  // 6. Beat detection using rising edge of normalized signal
  if (!BeatDetected && NormalizedSignal > 50 && LastNormalized <= 50) {
    unsigned long now = millis();
    BeatInterval = now - LastBeatTime;

    // Only count the beat if the interval is in a valid range
    if (BeatInterval >= 300 && BeatInterval <= 2000) {
      int bpm = 60000 / BeatInterval;
      HeartRate = (LastHeartRate * 7 + bpm) / 8;  // Smooth heart rate value
      LastHeartRate = HeartRate;
      LastBeatTime = now;
      BeatDetected = true;
      digitalWrite(LED_BUILTIN, HIGH);  // Blink LED on beat
    }
  }

  // 7. Reset the beat detection after the normalized signal goes below a threshold
  if (BeatDetected && NormalizedSignal < 50) {
    BeatDetected = false;
    digitalWrite(LED_BUILTIN, LOW);  // Turn off LED after beat
  }

  // 8. Output the heart rate if enough time has passed
  if (millis() - LastPrintTime >= PrintInterval) {
    LastPrintTime = millis();
    Serial.print(" | Heart Rate:  ");
    Serial.print(HeartRate);  // Print the heart rate
    Serial.println(" BPM");
  }

  LastNormalized = NormalizedSignal;  // Save the last normalized signal for future comparisons
  delay(50);  // Short delay to avoid spamming the serial output
}

// 🧠 Signal variance calculator
int getSignalVariance() {
  int minVal = 1023;
  int maxVal = 0;
  for (int i = 0; i < 20; i++) {  // Use larger buffer for better variance calculation
    if (SignalBuffer[i] < minVal) minVal = SignalBuffer[i];
    if (SignalBuffer[i] > maxVal) maxVal = SignalBuffer[i];
  }
  return maxVal - minVal;
}
