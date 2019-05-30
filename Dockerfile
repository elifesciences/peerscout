ARG commit=develop
FROM elifesciences/peerscout_client:${commit} AS client
FROM elifesciences/python:cacd250ec201feab491c0738f261561b5360997b

USER elife
ENV PROJECT_FOLDER=/srv/peerscout
RUN mkdir ${PROJECT_FOLDER}

ENV VENV=${PROJECT_FOLDER}/venv
RUN virtualenv ${VENV}
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

COPY --from=client --chown=elife:elife /home/node/client/ ${PROJECT_FOLDER}/client/
COPY --chown=elife:elife peerscout/ ${PROJECT_FOLDER}/peerscout/
COPY --chown=elife:elife server.sh ${PROJECT_FOLDER}/
COPY --chown=elife:elife update-data-and-reload.sh ${PROJECT_FOLDER}/
COPY --chown=elife:elife migrate-schema.sh ${PROJECT_FOLDER}/
COPY --chown=elife:elife app-defaults.cfg ${PROJECT_FOLDER}/

USER root
RUN mkdir .data && chown www-data:www-data .data
RUN mkdir logs && chown www-data:www-data logs

USER www-data
CMD ["venv/bin/python"]
