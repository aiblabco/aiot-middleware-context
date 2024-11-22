import pandas as pd
import get_config
import web_query
import time
import paho.mqtt.client as mqtt
import json

env_dict = get_config.get_env()

def upload_analysis_data(sensor_df):
    upload_url = env_dict['upload_analysis_url']
    upload_list = []
    id_list = sensor_df['smart_sensor_uid'].to_list()
    state_list = sensor_df['state'].to_list()
    cause_list = sensor_df['cause'].to_list()
    state_new_list = sensor_df['state_new'].to_list()
    cause_new_list = sensor_df['cause_new'].to_list()
    upload_index = 0

    mqtt_id = []
    mqtt_message = []
    mqtt_event = []
    timestamp = int(time.time())

    for i in range(len(sensor_df)):
        if state_list[i] == state_new_list[i]:
            if state_list[i] == 'N':
                continue
            elif cause_list[i] == cause_new_list[i]:
                continue
        now_list_str = 'list['+str(upload_index)+'].'
        upload_list.append((now_list_str+'smartSensorUid', id_list[i]))
        upload_list.append((now_list_str+'state', state_new_list[i]))
        if state_new_list[i] == 'N':
            upload_list.append((now_list_str+'cause', None))
        else:
            upload_list.append((now_list_str+'cause', cause_new_list[i]))
            if state_list[i] != state_new_list[i]:
                mqtt_id.append(id_list[i])
            if state_new_list[i] == 'A':
                mqtt_event.append('DEVICE-STATUS-ABNORMAL')
                mqtt_message.append('장치 상태가 장애상태로 감지되었습니다.')
            elif state_new_list[i] == 'C':
                mqtt_event.append('DEVICE-STATUS-CHECK')
                mqtt_message.append('장치 상태가 점검상태로 감지되었습니다.')
            else:
                mqtt_event.append('DEVICE-STATUS-FAIL')
                mqtt_message.append('장치 상태가 고장상태로 감지되었습니다.')
        upload_index = upload_index + 1

    if len(upload_list) > 0:
        result = web_query.web_request_retry('post', upload_url, upload_list)
        print(result.status_code)
    if len(mqtt_id) > 0:
        # MQTT 클라이언트 생성
        client = mqtt.Client()
        broker_address = env_dict['broker_address']
        broker_port = env_dict['broker_port']
        broker_topic = env_dict['broker_topic']
        # MQTT 브로커에 연결
        client.connect(broker_address, broker_port)
        for i in range(len(mqtt_id)):
            data = {
                "serviceOrigin" : "fims-analysis-ai",
                "eventType" : mqtt_event[i],
                "uid" : mqtt_id[i],
                "message" : mqtt_message[i],
                "timestamp" : timestamp
            }
            message = json.dumps(data, ensure_ascii=False).encode('utf-8')
            client.publish(broker_topic, message)
        client.disconnect()