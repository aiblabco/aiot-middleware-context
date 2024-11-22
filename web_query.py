import requests
import time
import get_config

env_dict = get_config.get_env()
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

def get_request(url, post_json=None):
    if post_json == None:
        r = requests.get(url)
    else:
        r = requests.get(url, params=post_json)
    return r

def post_request(url, post_json=None):
    if post_json == None:
        r = requests.post(url)
    else:
        r = requests.post(url, data=post_json, headers=headers)
    return r

def web_request_retry(type, url, post_json=None):
    """timeout발생 시 sleep_seconds쉬고 num_retyrp번 재시도 한다"""
    for n in range(300):
        try:
            if type == 'get':
                return get_request(url, post_json)
            else:
                return post_request(url, post_json)
        except Exception as err:
            last_err = err
            print(str(n+1) + ' Timeout')
            print(last_err)
            time.sleep(1)
            continue
    return None