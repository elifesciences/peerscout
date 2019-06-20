ARG commit=develop
FROM elifesciences/peerscout_client:${commit} AS client
FROM elifesciences/python_3.6:6f4c43c064fe45e0a158694fbdad9e473dbcad87

USER root
RUN apt-get update && \
    apt-get -y install gcc g++ && \
    rm -rf /var/lib/apt/lists/*

USER elife
ENV PROJECT_FOLDER=/srv/peerscout
RUN mkdir ${PROJECT_FOLDER}

ENV VENV=${PROJECT_FOLDER}/venv
RUN python -m venv ${VENV}
ENV PYTHONUSERBASE=${VENV} PATH=${VENV}/bin:$PATH

WORKDIR ${PROJECT_FOLDER}

COPY --chown=elife:elife requirements.spacy.txt ${PROJECT_FOLDER}/
RUN pip install -r requirements.spacy.txt
RUN python -m spacy download en

COPY --chown=elife:elife requirements.prereq.txt ${PROJECT_FOLDER}/
RUN pip install -r requirements.prereq.txt

COPY --chown=elife:elife requirements.txt ${PROJECT_FOLDER}/
RUN pip install -r requirements.txt

ARG install_dev
COPY requirements.dev.txt ./
RUN if [ "${install_dev}" = "y" ]; then pip install -r requirements.dev.txt; fi

COPY --from=client --chown=elife:elife /home/node/client/dist/ ${PROJECT_FOLDER}/client/dist/
COPY --chown=elife:elife peerscout/ ${PROJECT_FOLDER}/peerscout/
COPY --chown=elife:elife server.sh ${PROJECT_FOLDER}/
COPY --chown=elife:elife update-data-and-reload.sh ${PROJECT_FOLDER}/
COPY --chown=elife:elife migrate-schema.sh ${PROJECT_FOLDER}/
COPY --chown=elife:elife app-defaults.cfg ${PROJECT_FOLDER}/

USER root
RUN mkdir .data && chown www-data:www-data .data
RUN mkdir logs && chown www-data:www-data logs && chmod -R a+w logs

USER www-data
CMD ["/srv/peerscout/server.sh"]
