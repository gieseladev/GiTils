FROM python:alpine

LABEL maintainer="Simon (siku2)"

WORKDIR /install_temp
RUN apk update &&\
 apk add gcc linux-headers musl-dev unzip

# Install master branch of Vibora
RUN wget https://github.com/vibora-io/vibora/archive/master.zip -O vibora.zip &&\
 unzip vibora.zip &&\
 cd ./vibora-master &&\
 pip install -r requirements.txt &&\
 python build.py &&\
 pip install .

COPY Pipfile ./
COPY Pipfile.lock ./

RUN pip install pipenv
RUN pipenv install --system --deploy
RUN rm -rf /install_temp

WORKDIR /gitils
COPY gitils gitils

ENTRYPOINT ["python", "gitils"]