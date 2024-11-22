import pandas as pd
import analysis_sensor
import get_sensor
import upload_analysis

if __name__ == '__main__':
    sensor_df = get_sensor.get_sensor_list()
    if len(sensor_df) == 0:
        exit()

    sensor_df = analysis_sensor.analysis_status(sensor_df)

    upload_analysis.upload_analysis_data(sensor_df)

