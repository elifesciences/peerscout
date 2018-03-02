elifePipeline({
    def commit
    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    elifeOnNode(
        {
            stage 'Build image', {
                checkout scm
                sh "docker build -f Dockerfile.client -t elifesciences/peerscout_client:${commit} ."
                sh "docker build -f Dockerfile -t elifesciences/peerscout:${commit} --build-arg commit=${commit} ."
            }

            stage 'Project tests (container)', {
                sh "docker run elifesciences/peerscout_client:${commit} ./project_tests.sh"
                dockerBuildCi 'peerscout', commit

                // substitute with:
                // dockerProjectTests 'peerscout', commit, ['build/pytest.xml']
                // when correctly using `docker cp` on build/
                sh "docker run elifesciences/peerscout_ci:${commit}"
            }
        },
        'containers--medium'
    )

    stage 'Project tests', {
        lock('peerscout--ci') {
            builderDeployRevision 'peerscout--ci', commit
            builderSmokeTests 'peerscout--ci', '/srv/peerscout'
        }
    }

    stage 'End2end', {
        lock('peerscout--end2end') {
            builderDeployRevision 'peerscout--end2end', commit
            builderSmokeTests 'peerscout--end2end', '/srv/peerscout'
            builderCmd 'peerscout--end2end', './update-data-and-reload.sh', '/srv/peerscout'
        }
    }

    elifeMainlineOnly {
        stage 'Approval', {
            elifeGitMoveToBranch commit, 'approved'
        }
    }
}, 360)
