import random
import get_sensor
from datetime import datetime
import numpy as np

def check_anomalies(df, column_name, period_data_count):
    # 이동 평균 계산
    df['Moving_Avg'] = df[column_name].rolling(window=period_data_count, min_periods=1).mean()

    # 전체 데이터에 대한 표준편차 계산
    std_dev = df[column_name].std()

    # 상한과 하한 범위 계산 (이동 평균 ± 3 시그마)
    df['Upper_Bound'] = df['Moving_Avg'] + 3 * std_dev
    df['Lower_Bound'] = df['Moving_Avg'] - 3 * std_dev

    # 이상치 존재 여부 확인
    df['Anomaly'] = (df[column_name] > df['Upper_Bound']) | (df[column_name] < df['Lower_Bound'])
    has_anomalies = df['Anomaly'].any()

    return has_anomalies

def analysis_status(sensor_df):
    # 현재 아무 처리 없이 랜덤하게 생성
    sensor_list = sensor_df['smart_sensor_uid'].to_list()
    analysis_list = []
    cause_list = []

    for i in range(len(sensor_list)):
        now_sensor = sensor_list[i]
        to_date = datetime.now()
        now_sensor_df, now_term = get_sensor.get_sensor_data(now_sensor, to_date)
        if now_sensor_df is None:
            if now_term == 0:
                analysis_list.append('N')
                cause_list.append('')
            elif now_term == 1:
                analysis_list.append('F')
                cause_list.append('데이터 수신 없음')
            elif now_term == 2:
                analysis_list.append('A')
                cause_list.append('통신 이상-데이터 결측')
            elif now_term == 3:
                analysis_list.append('A')
                cause_list.append('통신 이상-데이터 누락')
            continue

        if np.isinf(now_sensor_df.values).any():
            # inf값이 포함된 경우
            analysis_list.append('A')
            cause_list.append('통신 이상-측정범위 외')
            continue
        elif now_sensor_df.isna().any().any():
            # na값이 포함된 경우
            analysis_list.append('A')
            cause_list.append('통신 이상-데이터 누락')
            continue
        col_list = now_sensor_df.columns
        for i in range(len(col_list)):
            if check_anomalies(now_sensor_df, col_list[i], int(21600/now_term)):
                analysis_list.append('A')
                cause_list.append('데이터 이상-이상치 발생')
                break
            else:
                if i == len(col_list)-1:
                    analysis_list.append('N')
                    cause_list.append('')

    sensor_df['state_new'] = analysis_list
    sensor_df['cause_new'] = cause_list

    return sensor_df