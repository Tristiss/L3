int num = 0;

void setup() {
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg == "0") {
      if (num == 0) {
        num = 1;
        digitalWrite(7, HIGH);
        digitalWrite(8, LOW);
      } else {
        num = 0;
        digitalWrite(7, LOW);
        digitalWrite(8, HIGH);
      }
      Serial.println("OK");
    }
  }
}
