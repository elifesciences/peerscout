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
                dockerBuild 'peerscout', commit
            }

            stage 'Project tests (container)', {
                dockerProjectTests 'peerscout', commit
            }
        },
        'containers--medium'
    )

    stage 'Project tests', {
        lock('peerscout--ci') {
            builderDeployRevision 'peerscout--ci', commit

            builderProjectTests 'peerscout--ci', '/srv/peerscout'
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
