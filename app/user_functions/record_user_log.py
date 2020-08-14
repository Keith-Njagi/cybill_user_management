import requests
log_submission_url = 'https://c449b5121152.ngrok.io//api/logs' # 'http://0.0.0.0:3100/api/logs'

def record_user_log(auth_token, method, description):
    payload = {'method': method, 'description': description}

    res = requests.post(log_submission_url, json=payload, headers=auth_token)
    if res.status_code != 201:
        print ("Error:", res.status_code)
        print(res.text)
        return {'Message': description + ', but log was never recorded in database.'}, 400 