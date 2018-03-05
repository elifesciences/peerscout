ARG commit=develop
FROM elifesciences/peerscout_client:${commit} AS client
FROM elifesciences/python:cacd250ec201feab491c0738f261561b5360997b

USER elife
ENV PROJECT_FOLDER=/srv/peerscout
RUN mkdir ${PROJECT_FOLDER}
WORKDIR ${PROJECT_FOLDER}
COPY --chown=elife:elife install.sh requirements.txt ${PROJECT_FOLDER}/
RUN DEBUG=0 /bin/bash install.sh

COPY --from=client --chown=elife:elife /home/node/client/ ${PROJECT_FOLDER}/client/
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
ENV COVERAGE_FILE=${PROJECT_FOLDER}/build/.coverage
RUN touch app.cfg && chown www-data:www-data app.cfg

USER www-data
CMD ["venv/bin/python"]
