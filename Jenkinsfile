elifePipeline({
    def commit

    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    node('containers-jenkins-plugin') {
        stage 'Build and run tests', {
            checkout scm
            try {
                sh "make IMAGE_TAG=${commit} ci-build-and-test"
            } finally {
                sh "make ci-clean"
            }
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
