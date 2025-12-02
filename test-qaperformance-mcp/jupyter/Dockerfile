FROM jupyter/scipy-notebook:latest

USER root

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER jovyan

# Copiar requirements y instalar
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Configurar JupyterLab extensions
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build && \
    jupyter lab build --dev-build=False --minimize=False

# Crear directorio de trabajo
WORKDIR /home/jovyan/work

# Configurar Jupyter para permitir conexiones externas sin auth
RUN jupyter notebook --generate-config && \
    echo "c.NotebookApp.allow_origin = '*'" >> /home/jovyan/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.allow_remote_access = True" >> /home/jovyan/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.token = ''" >> /home/jovyan/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.password = ''" >> /home/jovyan/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.disable_check_xsrf = True" >> /home/jovyan/.jupyter/jupyter_notebook_config.py

EXPOSE 8888

# Comando por defecto sin token ni password
CMD ["start-notebook.sh", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]