pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.8' // Set the Python version you need
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    // Step 1: Check out the source code from the repository
                    checkout scm
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    // Step 2: Install Python and required dependencies
                    sh "pyenv global ${PYTHON_VERSION}"
                    sh 'pip install -r requirements.txt'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Step 3: Run Pytest and generate JUnit XML reports
                    sh 'pytest --junitxml=test-results.xml test_database.py'
                }
            }
        }
    }

    post {
        always {
            script {
                // Step 4: Archive JUnit XML test results for historical tracking
                junit 'test-results.xml'
            }
        }
        success {
            script {
                // Step 5: Archive and publish HTML test report on successful build
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'index.html',
                    reportName: 'Test Results'
                ])
            }
            echo 'Build succeeded! Additional success actions can be added here.'
        }
        failure {
            script {
                // Step 6: Archive and publish HTML test report on build failure
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'index.html',
                    reportName: 'Test Results'
                ])
                echo 'Build failed! Additional failure actions can be added here.'
            }
        }
    }
}
