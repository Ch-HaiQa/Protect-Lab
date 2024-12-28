pipeline {
    agent any
    stages {
        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                // sh 'npm install' // Example command for Node.js. Adjust for your project (e.g., `mvn install` for Java or `pip install` for Python).
            }
        }
        stage('Build') {
            steps {
                echo 'Building the application...'
                //sh 'npm run build' // Adjust for your project
            }
        }
        stage('Run Unit Tests') {
            steps {
                echo 'Running unit tests...'
                //sh 'npm test' // Adjust for your project
            }
        }
        stage('Test') {
            when {
                allOf {
                    expression {
                        env.BRANCH_NAME == 'main' // Condition: Only run on 'main' branch
                    }
                    //environment name: 'RUN_TESTS', value: 'true' // Condition: Environment variable must be 'true'
                }
            }
            steps {
                echo 'Running additional tests...'
                //sh 'npm run test:integration' // Adjust for your project
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                //sh './deploy.sh' // Replace with your deployment script or commands
            }
        }
    }
}
