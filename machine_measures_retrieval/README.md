GeneratedGetMeasuresCSV
=======================

Este script tiene como objetivo:
* Ejecutar el comando sobre la máquina remota que genera las métricas como CSV (encapsulando el sadf)
* Trasladar las métricas desde el equipo remoto al equipo local
* Procesar este fichero remoto adaptando la salida a lo que espera nuestra BD (InfluxDB)
* Guarda las evidencias en un directorio local (fichero en bruto y fichero transformado)
* [En un futuro] Lanzará o integrará el script que introduce estas medidas en InfluxDB

Uso
---

Actualmente se ejecuta automaticamente desde el docker desplegado en la máquina inyectora

python MachineMeasuresRetrieval.py
python MachineMeasuresRetrieval.py -s 10:00:00 -e 12:00:00
python MachineMeasuresRetrieval.py -s 10:00:00 -e 12:00:00

Toda la configuracion del sistema se realiza desde el fichero properties.ini.

Antes se necesita:
* Instalar en la máquina remota el paquete sysstat y levantar el servicio asociado
* Configurar en la máquina remota la utilidad SAR en el fichero crontab 
* Comprobar que los métodos de conexión con la máquina remota estan habilitados (user/pass o mediante certificado)


Pendiente
---------

* Concretar el fichero de metricas de salida en relacion al grafana y al qareporter. AHora mismo y a modo de ejemplo:
    * Se pueden cambiar el orden de las columnas respecto a una lista
    * Omitir determinadas columnas en el fichero procesado (con alguna restriccion) respecto a una lista
    * Cambiar el formato del timestamp
* Lanzar la aplicacion csv-to-influxdb para introducir las metricas en el influxdb


Pasos para parametrizar por línea de comandos las direcciones del SUT
---------------------------------------------------------------------

* Añadir en el fichero  _wt_performance/project-example/Jenkinsfile_ los comandos
  ~~~
  parameters([
        string(defaultValue: "master", description: 'Branch to build', name: 'GIT_BRANCH'),
        ...
        choice(choices: ["No", "Yes"].join("\n"), description: 'Obtain host machine measures', name: 'PERFORMANCE_OBTAIN_HOST_MEASURES'),
        string(defaultValue: "176.34.141.185", description: 'Remote host address -, as separator-', name: 'PERFORMANCE_SUT_ADDRESS'),
        string(defaultValue: "ubuntu", description: 'Users for remote hosts -, as separator-', name: 'PERFORMANCE_SUT_USERNAMES')
  ])
  ~~~
  Asi añadimos los parametros al job de DCIP
  
  Es interesante, para _tracear_ la ejecución añadir tambien las entradas
  ~~~
        ...
        echo "remote hosts: ${env.GIT_BRANCH}"
        echo "remote usernames: ${env.PERFORMANCE_SUT_ADDRESS}"
        echo "Running ${env.BUILD_ID} on ${env.PERFORMANCE_SUT_USERNAMES}"
  ~~~

* Reemplazar en el fichero  _wt_performance/project-example/run-jmeter-remote-slave.sh_ la línea
  ~~~
  sudo python MachineMeasuresRetrieval.py -s ${START_TIME} -e ${END_TIME} -path /tmp/qacdo/performance/machine_measures_retrieval/${FOLDER_ID}
  ~~~
  por la siguiente
  ~~~
  sudo python MachineMeasuresRetrieval.py -s ${START_TIME} -e ${END_TIME} -path /tmp/qacdo/performance/machine_measures_retrieval/${FOLDER_ID} -a ${PERFORMANCE_SUT_ADDRESS} -u ${PERFORMANCE_SUT_USERNAMES}
  ~~~



Notas
---------

* Si tanto como el inyector como la máquina a probar están en la misma subred, hay que usar la ip privada
en vez de la pública. Esto es especialmente importante al usar máquinas AWS.

* Si al ejecutar MachineMeasuresRetrieval.py sale un error OutOfIndex, es debido a que no hay métricas que recoger 
en las horas seleccionadas. Este problema ocurre principalmente porque las máquinas se encuentran apagadas 
en ese intervalo. (Cuidado con las horas locales en las diferentes máquinas)
