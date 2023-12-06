pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.8' // Set the Python version you need
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    // Install Python and required dependencies
                    sh "pyenv global ${PYTHON_VERSION}"
                    sh 'pip install -r requirements.txt'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run your Pytest script
                    sh 'pytest test_database.py'
                }
            }
        }
    }

    post {
        always {
            // Clean up steps, if needed
        }
        success {
            // Actions to perform on successful build
        }
        failure {
            // Actions to perform on build failure
        }
    }
}
