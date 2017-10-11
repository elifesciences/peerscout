elifePipeline({
    def commit
    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    stage 'Project tests', {
        lock('peerscout--ci') {
            builderDeployRevision 'peerscout--ci', commit

            // remove when builderProjectTests is in, as smoke tests are already run by builderProjectTests itself
            builderSmokeTests 'peerscout--ci', '/srv/peerscout'

            //builderProjectTests 'peerscout--ci', '/srv/peerscout'
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
