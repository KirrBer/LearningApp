import requests

def get_vacancies(text='', per_page=100, professional_role=11):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'text': text,
        'per_page': per_page,
        'professional_role': professional_role
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = [item['id'] for item in response.json().get('items', [])]
        return result
    else:
        print(f"Error: {response.status_code}")
        return []
def get_vacancy(id):
    url = f'https://api.hh.ru/vacancies/{id}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            'id': data['id'],
            'name': data['name'],
            'description': data['description'],
            'employer': data['employer']['name'],
            'salary': data.get('salary'),
            'employment': data.get('employment', {}).get('name'),
            'schedule': data.get('schedule', {}).get('name'),
            'experience': data.get('experience', {}).get('name'),
            'area': data['area']['name']
        }
    else:
        print(f"Ошибка {response.status_code}")
        return None
