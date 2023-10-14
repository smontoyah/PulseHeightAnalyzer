const byte signalPin = 2; // Pin de entrada de la señal
volatile unsigned int pulseCount = 0; // Contador de pulsos
unsigned long previousMillis = 0; // Tiempo en milisegundos del último cambio de umbral
unsigned long tw = 0; // Tiempo en milisegundos entre cambios de umbral
unsigned long t_max = 0; // Tiempo máximo de ejecución en milisegundos
const int th_step = 1; // L and U thereshold steps. DAC value (8 bits)
int th_diff = 1; //Threshold difference. DAC value (8bits)
int data_size = 255-th_diff;
unsigned int th_low = 0; // Umbral inferior (8 bits)
unsigned int th_high = th_low + th_diff; // Umbral superior (8 bits)
String datos[255];
unsigned long counts[255];


void setup() {
  Serial.begin(115200); // Iniciar comunicación serial
  pinMode(signalPin, INPUT_PULLUP); // Configurar pin de entrada de la señal como pull-up
  attachInterrupt(digitalPinToInterrupt(signalPin), pulse, RISING); // Configurar interrupción en el pin de entrada de la señal
}

void loop() {
  if (Serial.available() > 0) { // Si hay datos en el puerto serial
    String command = Serial.readStringUntil('\n'); // Leer el comando
    if(command.startsWith("L")){
      int L = command.substring(1).toInt(); // Obtener el valor de L (lower level)
      dacWrite(26, L);
      Serial.print("L");Serial.println(L);
    } else if(command.startsWith("U")){
      int U = command.substring(1).toInt(); // Obtener el valor de L (lower level)
      dacWrite(25, U);
      Serial.print("U");Serial.println(U);
    } else if(command.startsWith("thd")){
      th_diff = command.substring(3).toInt(); // Obtener el valor de L (lower level)
      data_size = 255-th_diff;
      dacWrite(25, th_diff); //Set the initial values before starting
      dacWrite(26, 0);
      delay(100);
    }else if (command.startsWith("tw")) { // Si el comando es para configurar tw
      tw = command.substring(2).toInt(); // Obtener el valor de tw
    } else if (command.startsWith("ts")) { // Si el comando es para configurar t_max
      t_max = command.substring(2).toInt(); // Obtener el valor de t_max
    } else if (command.equals("start")) { // Si el comando es para iniciar la ejecución
      dacWrite(25, th_diff);
      dacWrite(26, 0);
      pulseCount=0; //Reinicia conteo
      delay(1000);
      unsigned long startTime = millis(); // Obtener el tiempo de inicio
      while (millis() - startTime < t_max) { // Ejecutar durante t_max milisegundos
        if (millis() - previousMillis >= tw) { // Si ha pasado el tiempo de cambio de umbral
          unsigned int accCounts=counts[th_low]+pulseCount; //Invrementar las cuentas acumuladas con el valor contado
          counts[th_low]=accCounts; //actualiza el arreglo de cuentas acumuladas 
           // Agregar datos al arreglo
          datos[th_low] = String(th_low) + "*" + String(accCounts);
          previousMillis = millis(); // Actualizar el tiempo del último cambio de umbral
          dacWrite(25, th_high);
          dacWrite(26, th_low);     
          th_low += th_step; // Incrementar umbral inferior
          th_high += th_step; // Incrementar umbral superior
          pulseCount = 0; // Reiniciar el contador de pulsos
          //Serial.print(th_low); //Only for debugging
          //Serial.print("\t");
          //Serial.println(th_high); //Only for debugging
          // Enviar datos por serial cuando th_high llega a 256
          if (th_low == data_size+1) {
            //Serial.println("Enviando datos por serial...");
            for (int i = 0; i < data_size; i++) {
              Serial.print(datos[i]);
              Serial.print(",");
            }
            Serial.println();
            th_low = 0; // Reiniciar umbral inferior
            th_high = th_low + th_diff; // Reiniciar umbral superior
          }
        }
        if (millis() - startTime >= t_max) { // Si se llegó a t_max
          Serial.println("finished"); // Enviar "finished" por serial
          th_low = 0; // Reiniciar umbral inferior
          th_high = th_low + th_diff; // Reiniciar umbral superior
          dacWrite(25, th_high);
          dacWrite(26, th_low);
          startTime=millis();
          //Clear the counts array:
          for (int i=0; i < data_size ; i++){
            counts[i]=0;
          }
          break; // Salir del bucle while
        }
      }
    }
  }
}

void pulse(){
  pulseCount++;
}
