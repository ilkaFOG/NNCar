#include <NewPing.h> // Подключаем библиотеку для работы с ультразвуковым датчиком
#include <NeuralNetwork.h> // Подключаем библиотеку для работы с нейронной сетью
#include <Servo.h> // Подключаем библиотеку для работы с сервоприводом

#define TRIGGER_PIN 8 // Номер пина, к которому подключен триггер ультразвукового датчика
#define ECHO_PIN 8 // Номер пина, к которому подключен эхо ультразвукового датчика
#define MAX_DISTANCE 400 // Максимальное расстояние для измерения в сантиметрах

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // Создаем объект для работы с ультразвуковым датчиком
NeuralNetwork nn(3, 4, 2); // Создаем нейронную сеть с 3 входами, 4 скрытыми слоями и 2 выходами
Servo myservo; // Создаем объект для работы с сервоприводом

const int FwdPin_A = 0; 
const int BwdPin_A = 1;  
const int FwdPin_B = 2; 
const int BwdPin_B = 3;        

int MaxSpd = 100;               // Скорость, значение 0-255
float distance;

void setup()
{
  pinMode(FwdPin_A, OUTPUT);    // Устанавливаем FwdPin_A как выход
  pinMode(BwdPin_A, OUTPUT);    // Устанавливаем BwdPin_A как выход
  pinMode(FwdPin_B, OUTPUT);    // Устанавливаем FwdPin_B как выход
  pinMode(BwdPin_B, OUTPUT);    // Устанавливаем BwdPin_B как выход
  myservo.attach(10); // Подключаем сервопривод к пину 3
  Serial.begin(9600); // Инициализируем последовательный порт для вывода данных
}

void loop()
{
  delay(50); // Задержка для стабилизации показаний датчика

  for (int i = 45; i <= 135; i+=45) {
    myservo.write(i);
    delay(100);
    distance = sonar.ping_cm();
    delay(20);}

  float inputs[3] = {distance, 0, 0}; // Формируем массив входных данных для нейронной сети

  float *outputs = nn.FeedForward(inputs); // Получаем выходные данные нейронной сети

  int leftMotorSpeed = map(outputs[0], 0, 1, 0, 255); // Преобразуем выходные данные нейронной сети в скорость левого двигателя
  int rightMotorSpeed = map(outputs[1], 0, 1, 0, 255); // Преобразуем выходные данные нейронной сети в скорость правого двигателя

  analogWrite(FwdPin_A, leftMotorSpeed); // Устанавливаем скорость левого двигателя
  analogWrite(BwdPin_A, 0); // Отключаем торможение левого двигателя

  analogWrite(FwdPin_B, rightMotorSpeed); // Устанавливаем скорость правого двигателя
  analogWrite(BwdPin_B, 0); // Отключаем торможение правого двигателя

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.print(" Left motor speed: ");
  Serial.print(leftMotorSpeed);
  Serial.print(" Right motor speed: ");
  Serial.println(rightMotorSpeed);
}