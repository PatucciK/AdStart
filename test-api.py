import requests

# URL API
BASE_URL = 'http://127.0.0.1:8000/accounts/api/'
REQUEST_CONFIRMATION_CODE_URL = f'{BASE_URL}request-confirmation-code/'
CONFIRM_EMAIL_AND_REGISTER_URL = f'{BASE_URL}confirm-email/'

# Данные для запроса кода подтверждения
email_data = {
    'email': 'advertiser@example.com',
}

# Данные для подтверждения email и регистрации
confirmation_data_advertiser = {
    'email': 'advertiser@example.com',
    'confirmation_code': '',  # Код будет введен пользователем
    'user_type': 'advertiser',
    'password': 'password123',
    'telegram': '@advertiser',
    'phone': '1234567890'
}

def request_confirmation_code():
    response = requests.post(REQUEST_CONFIRMATION_CODE_URL, json=email_data)
    print('Request Confirmation Code Response:')
    print('Status Code:', response.status_code)
    print('Response Data:', response.json())

def confirm_email_and_register(confirmation_code):
    confirmation_data_advertiser['confirmation_code'] = confirmation_code
    response = requests.post(CONFIRM_EMAIL_AND_REGISTER_URL, json=confirmation_data_advertiser)
    print('Confirm Email and Register Response:')
    print('Status Code:', response.status_code)
    print('Response Data:', response.json())

if __name__ == '__main__':
    request_confirmation_code()
    confirmation_code = input("Enter the confirmation code received via email: ")
    confirm_email_and_register(confirmation_code)
