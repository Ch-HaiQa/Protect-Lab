pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building..'
                // Here you can define commands for your build
            }
        }
        stage('Test') {
            when {
                allOf {
                    expression {
                        // Condition 1: Run only if the branch is 'main'
                        env.BRANCH_NAME == 'main'
                    }
                    environment name: 'RUN_TESTS', value: 'true'
                }
            }
            steps {
                echo 'Testing..'
                // Here you can define commands for your tests
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
                // Here you can define commands for your deployment
            }
        }
    }
}
