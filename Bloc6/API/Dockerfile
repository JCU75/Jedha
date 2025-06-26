FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update -y 
RUN apt-get install nano unzip
RUN apt install curl -y

# Create Conda environment with Python 3.10.12
RUN conda create -n myenv python=3.10.12
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

RUN curl -fsSL https://get.deta.dev/cli.sh | sh

COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

COPY . /home/app

# Use shell script to manage environment variable
COPY start.sh /home/app/start.sh
RUN chmod +x /home/app/start.sh

CMD ["/home/app/start.sh"]