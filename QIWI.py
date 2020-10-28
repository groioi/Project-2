import requests
import json
import urllib3
# История платежей - последние и следующие n платежей
def payment_history_last(my_login, api_access_token, rows_num, next_TxnId, next_TxnDate):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token
    parameters = {'rows': rows_num, 'nextTxnId': next_TxnId, 'nextTxnDate': next_TxnDate}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + my_login + '/payments', params = parameters, verify=False)
    return h.json()



# токен КИВИ и номер телефона
api_access_token = 'e30683c72403dba0142bbdb4e31414a7'
my_login = '+79299779008'
# кол-во перводов
rows_num = "1"
# за какой промежуток времени
next_TxnId, next_TxnDate = "",""

profile = payment_history_last(my_login, api_access_token, rows_num, next_TxnId, next_TxnDate)

# вводит сумму последнего платежа и комментарий к нему
# sum = profile['data'][0]['sum']['amount'] # int
# comment = profile['data'][0]['comment']
# number_phone = profile['data'][0]['account']
# number_phone_1 = str(number_phone)
# number_phone_1 = list(number_phone)
# number_phone_1.remove('+')
# number_phone_1 = ''.join(number_phone_1)
# print(number_phone_1)
