# INSTRUCCIONES DE EJECUCIÓN
1. Encender el injector a utilizar:
    * Ir al siguiente enlace del job de jenkins [Link](https://pro-dcip-qacdo-01.hi.inet/job/WT_INFRASTRUCTURE/job/WTI_DEVOPS_AWS_start_stop_instances), hacer click en "Build with Parameters" del panel de la izquierda, seleccionar "***start***", el inyector "***qacdo-es-pro-performance-inj01***" y ejecutar el build.

    * Recoger la ip pública que se le otorga a este inyector en el console output del build.

2. Ejecución del job:
    * En el siguiente job de jenkins [link](https://pro-dcip-qacdo-01.hi.inet/job/WT_PERFORMANCE/job/locust_infra_test), hacer click en "***Build with Parameters***" del panel de la izquierda. Rellenar el parámetro "**HOST_INJECTOR**" con la ip del inyector a utilizar. El resto de parámetros pueden ser modificados según convenga, pero con los seteados por defecto, el test es funcional.

3. Revisión de resultados:
    Aunque en nuestros pipelines se generan gráficas de resultados. Lo ideal es ir al [Performance Reporter](http://qacdco.hi.inet/pre-performance/reporter/projects) de PRE en este caso, y acceder a la ejecución realizada dentro del proyecto LOCUST para un mejor análisis.