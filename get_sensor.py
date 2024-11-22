import io
import datetime
import get_config
import web_query
import pandas as pd
from datetime import datetime, timedelta
import json

env_dict = get_config.get_env()

def find_term(datetime_list):
    # 리스트가 두 개 이상의 datetime 객체를 가지고 있는지 확인
    if len(datetime_list) < 2:
        return -1

    # 각 datetime 객체 간 초 단위의 시간 격차 계산
    time_gaps = [
        (datetime_list[i] - datetime_list[i+1]).total_seconds()
        for i in range(len(datetime_list) - 1)
    ]
    # 모든 시간 격차가 동일한지 확인
    if all(gap == time_gaps[0] for gap in time_gaps):
        return time_gaps[0]
    else:
        return -1

def get_sensor_list():
    get_analysis_url = env_dict['get_analysis_url']
    analysis_request = web_query.web_request_retry('get', get_analysis_url).json()

    if analysis_request['header']['status'] != 200:
        return None
    sensor_df = pd.json_normalize(analysis_request['body']['data'])
    sensor_df = sensor_df[['smart_sensor_uid']]
    return sensor_df

def get_sensor_data(sensor_id, to_date, sensor_type=201):
    # 실제 데이터 수신
    get_data_url = env_dict['get_data_url']
    from_date = to_date - timedelta(days=2)
    get_data_url = get_data_url + str(sensor_type) + '/smart_sensor_uid/' + str(sensor_id) + \
                   '/from/' + from_date.strftime('%Y-%m-%d') + '/to/' + to_date.strftime('%Y-%m-%d')
    data_request = web_query.web_request_retry('get', get_data_url).json()
    # 고장 판단
    if data_request['header']['status'] != 200:
        return None, 1
    sensor_data_df = pd.json_normalize(data_request['body']['data'])
    # 고장 판단
    if len(sensor_data_df) == 0:
        return None, 1

    sensor_value_list = sensor_data_df['value'].to_list()
    # 데이터 결측
    if len(sensor_data_df) == 0:
        return None, 2
    sensor_value_json = [json.loads(item) for item in sensor_value_list]
    sensor_value_df = pd.json_normalize(sensor_value_json)
    sensor_value_df = sensor_value_df.astype(float)
    # 정상 판단
    if len(sensor_value_df) == 1:
        return None, 0
    local_timezone = datetime.now().astimezone().tzinfo
    reported_list = pd.to_datetime(sensor_data_df['reported_at'], utc=True).dt.tz_convert(local_timezone).dt.tz_localize(None).to_list()
    print(reported_list[0], reported_list[-1])
    diff1 = (reported_list[0] - reported_list[1]).total_seconds()
    diff2 = (to_date - reported_list[0]).total_seconds()
    # 마지막 수집 후 수신되지 않음, 데이터 누락
    if diff2 > diff1:
        return None, 3
    # 데이터가 2건인 경우 마지막 수집이 정상적이므로 정상 판단
    if len(sensor_value_df) == 2:
        return None, 0
    now_term = find_term(reported_list)
    # 수집주기 불일치, 데이터 누락
    if now_term == -1:
        return None, 3
    diff1 = (reported_list[-1] - reported_list[0]).total_seconds()
    # 수집시간이 6시간보다 적으면 정상 판단
    if diff1 < 21600:
        return None, 0
    sensor_value_df['reported_at'] = reported_list
    # 수집주기에 따라 데이터 변형 처리
    sensor_value_df.set_index('reported_at', inplace=True)
    df_filtered = sensor_value_df.loc[from_date:to_date]
    return df_filtered, now_term
