#!groovy
// def DOCKER_IMAGES = ["python:3.5.5", "python:3.6.4", "python:3.6.5"]
DOCKER_IMAGES = ["python:3.6.5"]
DEVELOPERS = []


def get_stages(docker_image) {
    stages = {
        docker.image(docker_image).inside {

            // The following line causes a weird issue, where pip tries to 
            // install into /usr/local/... instead of the virtual env.
            // Any help figuring out what's happening is appreciated.
            //
            // def PYTHON_VENV = docker_image.replaceAll('[:.]', '') + 'venv'
            //
            // So we set it to 'venv' for all parallel builds now
            def PYTHON_VENV = 'venv'

            stage("${docker_image}") {
                echo "Running in ${docker_image}"
            }
            stage("Prepare") {
                sh "rm -rf ${PYTHON_VENV}"
                sh "python -m venv ${PYTHON_VENV}"
                sh """
                    . ${PYTHON_VENV}/bin/activate
                    pip install -U pip setuptools wheel
                """
            }
            stage("Install Deps") {
                try { 
                    sh """
                        . ${PYTHON_VENV}/bin/activate
                        make dependencies
                    """
                } catch (e) { 
                    sendMail("Install Dependencies Failed")
                    throw e
                }
            }
            stage("Install Dev Deps") {
                try { 
                    sh """
                        . ${PYTHON_VENV}/bin/activate
                        make dev-dependencies
                    """
                } catch (e) { 
                    sendMail("Install Dev Dependencies Failed")
                    throw e
                }
            }
            stage("Install") {
                try { 
                    sh """
                        . ${PYTHON_VENV}/bin/activate
                        make install
                    """
                } catch (e) { 
                    sendMail("Install Failed")
                    throw e
                }
            }
            stage('Test') {
                try { 
                    sh """
                        . ${PYTHON_VENV}/bin/activate
                        make test
                    """
                    junit 'junit.xml'
                    archive 'junit.xml'
                } catch (e) { 
                    sendMail("Test Suite Failed")
                    throw e
                }
            }
            stage('Coverage') {
                try { 
                    sh """
                        . ${PYTHON_VENV}/bin/activate
                        make test-cov
                    """
                    step([$class: 'CoberturaPublisher',
                            autoUpdateHealth: false,
                            autoUpdateStability: false,
                            coberturaReportFile: 'coverage.xml',
                            failNoReports: false,
                            failUnhealthy: false,
                            failUnstable: false,
                            maxNumberOfBuilds: 0,
                            onlyStable: false,
                            sourceEncoding: 'ASCII',
                            zoomCoverageChart: false])
                } catch (e) { 
                    sendMail("Coverage Failed")
                    throw e
                }
            }
            stage('Docs') {
                try {
                    sh """
                        . ${PYTHON_VENV}/bin/activate
                        cd doc
                        export MPLBACKEND="agg"
                        make html
                    """
                } catch (e) {
                    sendChatMessage("Building Docs Failed")
                    sendMail("Building Docs Failed")
                    throw e
                }
            }
            stage('Publishing Docs') {
                try {
                   publishHTML target: [
                       allowMissing: false,
                       alwaysLinkToLastBuild: false,
                       keepAll: true,
                       reportDir: 'doc/_build/html',
                       reportFiles: 'index.html',
                       reportName: 'Documentation'
                   ]
                } catch (e) {
                    sendChatMessage("Publishing Docs Failed")
                    sendMail("Publishing Docs Failed")
                }
            }
        }
    }
    return stages
}


node('master') {

    cleanWs()
    checkout scm

    def stages = [:]
    for (int i = 0; i < DOCKER_IMAGES.size(); i++) {
        def docker_image = DOCKER_IMAGES[i]
        stages[docker_image] = get_stages(docker_image)
    }

    parallel stages
}


def sendChatMessage(message, channel=CHAT_CHANNEL) {
    rocketSend channel: channel, message: "${message} - [Build ${env.BUILD_NUMBER} ](${env.BUILD_URL})"
}


def sendMail(subject, message='', developers=DEVELOPERS) {
    for (int i = 0; i < developers.size(); i++) {
        def developer = DEVELOPERS[i]
        emailext (
            subject: "$subject - Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
            body: """
                <p>$message</p>
                <p>Check console output at <a href ='${env.BUILD_URL}'>${env.BUILD_URL}</a> to view the results.</p>
            """,
            to: developer
        )    
    }
}
