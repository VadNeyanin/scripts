def call(Map config = [:]) {
    def defaults = [
        serviceName: 'currency',
        version: '0.1.0',
        author: 'v.neyanin',
        port: 8000,
        endpoint: '/info'
    ]
    
    def params = defaults + config
    
    stage('Smoke test') {
        sh """  echo \'{"version":"${params.version}","service":"${params.serviceName}","author":"${params.author}"}\' > correct_info.json
                wget -O test.json http://localhost:${params.port}${params.endpoint}
                cat test.json
                diff test.json correct_info.json"""
        echo "THE FIRST TEST SUCCESSED!!!"
    }
}