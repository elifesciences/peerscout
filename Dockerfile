FROM node:6.13.0-stretch AS client

# we don't have a elife base image yet for node, so we use directly the official one
USER node
RUN mkdir /home/node/client
WORKDIR /home/node/client
COPY --chown=node:node client/package.json /home/node/client/
RUN npm install

FROM elifesciences/python:cacd250ec201feab491c0738f261561b5360997b

USER elife
ENV PROJECT_FOLDER=/srv/peerscout
RUN mkdir ${PROJECT_FOLDER}
WORKDIR ${PROJECT_FOLDER}
COPY --chown=elife:elife install.sh requirements.txt requirements-debug.txt ${PROJECT_FOLDER}/
RUN /bin/bash install.sh

COPY --chown=elife:elife client/ ${PROJECT_FOLDER}/client/
COPY --chown=elife:elife docvec_model/ ${PROJECT_FOLDER}/docvec_model/
COPY --chown=elife:elife peerscout/ ${PROJECT_FOLDER}/peerscout/
COPY --chown=elife:elife server.sh ${PROJECT_FOLDER}/
COPY --chown=elife:elife project_tests.sh ${PROJECT_FOLDER}/
COPY --chown=elife:elife update-data-and-reload.sh ${PROJECT_FOLDER}/
COPY --chown=elife:elife migrate-schema.sh ${PROJECT_FOLDER}/
COPY --chown=elife:elife app-defaults.cfg ${PROJECT_FOLDER}/


USER root
RUN mkdir .data && chown www-data:www-data .data
RUN mkdir logs && chown www-data:www-data logs

# Test
COPY --chown=elife:elife pytest.ini ${PROJECT_FOLDER}/
RUN mkdir build && chown www-data:www-data build
ENV COVERAGE_FILE=${PROJECT_FOLDER}/build/.coverage
RUN touch app.cfg && chown www-data:www-data app.cfg

USER www-data
CMD ["venv/bin/python"]
