import os

def get_env():
    try:
        #k8s 기준
        api_host = os.environ['FIMS_ANALYSIS_TCP_ADDR']
        api_port = os.environ['FIMS_ANALYSIS_TCP_PORT']
    except:
        try:
            api_url = os.environ['FIMS_ANALYSIS_API']
            api_host = api_url.split(':')[0]
            api_port = api_url.split(':')[1]
        except:
            api_host = 'fims-dev.nip.io'
            api_port = '80'
    try:
        api_meta_url = os.environ['FIMS_METADATA_API']
        api_meta_host = api_meta_url.split(':')[0]
        api_meta_port = api_meta_url.split(':')[1]
    except:
        api_meta_host = 'fims-dev.nip.io'
        api_meta_port = '80'
    try:
        api_data_host = os.environ['FIMS_DATA_APP_SERVICE_HOST']
        api_data_port = os.environ['FIMS_DATA_APP_SERVICE_PORT']
    except:
        api_data_host = 'fims-dev.nip.io'
        api_data_port = '80'
    api_protocol = 'http'
    try:
        # MQTT_BROKER_URL = tcp://activemq.queue:80 필요시 나눠서 사용
        broker_url = os.environ['MQTT_BROKER_URL'].split('://')[1].split(':')
        broker_address = broker_url[0]
        broker_port = int(broker_url[1])
    except:
        broker_address = "activemq.nip.io"
        broker_port = 80

    broker_topic = 'fims_notification'
    analysis_url = api_protocol + '://' + api_host + ':' + api_port + '/api/v1/analysis/status'
    get_uid_url = api_protocol + '://' + api_meta_host + ':' + api_meta_port + '/api/v1/metadata/smart_sensor'
    get_analysis_url = analysis_url + '/recent'
    upload_analysis_url = analysis_url + '/list'
    get_data_url = api_protocol + '://' + api_data_host + ':' + api_data_port + '/api/v1/data/type/'
    env_dict = {
        'upload_analysis_url' : upload_analysis_url, 'get_analysis_url' : get_analysis_url, 'get_uid_url': get_uid_url,
        'broker_address' : broker_address, 'broker_port' : broker_port, 'broker_topic' : broker_topic,
        'get_data_url' : get_data_url
    }
    return env_dict
