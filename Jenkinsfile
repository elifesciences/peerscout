elifePipeline {
    def commit
    stage 'Checkout', {
        checkout scm
        commit = elifeGitRevision()
    }

    stage 'Project tests', {
        lock('reviewer-suggestions--ci') {
            builderDeployRevision 'reviewer-suggestions--ci', commit

            // remove when builderProjectTests is in, as smoke tests are already run by builderProjectTests itself
            builderSmokeTests 'reviewer-suggestions--ci', '/srv/reviewer-suggestions'

            //builderProjectTests 'reviewer-suggestions--ci', '/srv/reviewer-suggestions'
        }
    }

    elifeMainlineOnly {
        stage 'Approval', {
            elifeGitMoveToBranch commit, 'approved'
        }
    }
}
