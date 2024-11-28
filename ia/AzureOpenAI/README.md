In order to evaluate azure IA capabilities, follow the instructions below:

1. In Azure OpenAI Service console create an assistant with these prompt:

```bash
Sigue estos pasos:
* Filtra en un fichero todos los eventos cuyo label contenga AccountDashboardModuleAgent.1.getAccountModules_success y  Settings.3.getUserSettingsConfig  coge los datos de las columas timeStamp , label y  elapsed
* Con el fichero del punto anterior, sacame una grafica agrupado por label, con puntos (no me unas los puntos con lineas), del numero de eventos por segundo a lo largo del tiempo(columna timeStamp), agrupamelo en intervalos de 5 segundos. En el eje x pon la fecha en oblicuo para evitar que se solapen. En el eje y calculame los TPS(transacciones por segundo) teniendo en cuenta que lo has agrupado en intervalos de 5 segundos. Los colores de cada label son rojo y verde.
* Con el mismo fichero del punto primero, saca otra grafica de puntos, donde se calcule el percentil 90 del campo elapsed agrupado cada 5 segundos. El campo elapsed esta en milisegundos. Dibuja ademas  una linea horizontal de puntos de color rojo para p90= 1000, este será un umbral maximo del p90 que tendras en cuenta en las conclusiones finales. Añade esta linea a la leyenda con el titulo de umbal maximo.
* Haz un doc en formato word donde se incluyan estas graficas, y dime que problemas ves y que acciones habria que realizar. Con un titulo con portada creativa e  indice
* Escribe otro fichero con formato txt, donde aparezca unicamente 3 posibles opciones : "RESULTADO DEL TEST ES: OK" o "RESULTADO DEL TEST ES: FAIL" o "RESULTADO DEL TEST ES:  UNSTABLE" con este criterio: 
  1. OK si el 0,1% o menos de los valores de la grafica percentil 90 del tiempo de respuesta estan por debajo del umbral establecido 
  2. UNSTABLE si los valoresde la grafica percentil 90 del tiempo de respuesta estan entre 0,1% y 5%
  3. FAIL si es mayor del 5%
```

2. Create a env variable for the Azure OpenAI API key 


```bash
export AZURE_OPENAI_API_KEY=sk-xxxxxxxxxxxxxx
```

3.  Copy locust_results.csv file with locust results for a specific test in  content root folder
```bash
cp locust_results.csv ia/AzureOpenAI/Assistant
```

4. Run the following commands to start the test (modify absolute path to the assistants folder in your local machine):

```bash

docker build -t performanceanalizer:0.0.1 .
docker rm -f performanceanalizer; docker run -v .:/app --name performanceanalizer -e AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY performanceanalizer:0.0.1
```
These commands will create 2 images in img folder using Novum performance test example inside assistant, and a doc in docs folder with the results of the test.



