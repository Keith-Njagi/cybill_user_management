import requests

log_submission_url = 'http://127.0.0.1:3100/api/logs'

def record_user_log(user_id, method, description):
    payload = {'user_id':user_id, 'method': method, 'description': description}
    res = requests.post(log_submission_url, json=payload)
    if res.status_code != 201:
        print ("Error:", res.status_code)
        print(res.text)
        return {'Message': description + ', but log was never recorded in database.'}, 400 