pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'python setup.py develop'
            }
        }
        stage('Bump version') {
            steps {
                sh 'git config user.email "git@videt.cn"'
                sh 'git config user.name "git-auto"'
                sh 'bumpversion $bumpVersionPart --verbose'
            }
        }
        stage('Upload to pypi server') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'pypi', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                    sh 'devpi use http://pypi.devops.videt.cn'
                    sh 'devpi login videt --password="$PASSWORD"'
                    sh 'devpi use videt/repo'
                    sh 'devpi upload'
                }
            }
        }
        stage('Push to git repository') {
            steps {
                sh 'git push --all'
            }
        }
    }
}
