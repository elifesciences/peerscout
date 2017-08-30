elifePipeline {
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

    elifeMainlineOnly {
        stage 'Approval', {
            elifeGitMoveToBranch commit, 'approved'
        }
    }
}
