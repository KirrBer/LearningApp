import requests

def get_vacancies_id(page=0):
    url = 'https://api.hh.ru/vacancies'
    variants = "разработчик OR программист OR аналитик OR developer OR junior OR middle OR senior"
    params = {
        'text': variants,
        'per_page': 100,
        'page': page
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
            'id': int(data.get('id')),
            'name': data.get('name'),
            'description': data.get('description'),
            'employer': data.get('employer', {}).get('name') if data.get('employer') else 'не указано',
            'salary': ('от ' + str(data.get('salary', {}).get('from')) + ' до' + str(data.get('salary', {}).get('to'))) if data.get('salary') else 'не указано',
            'employment': data.get('employment', {}).get('name') if data.get('employment') else 'не указано',
            'schedule': data.get('schedule', {}).get('name') if data.get('schedule') else 'не указано',
            'experience': data.get('experience', {}).get('name') if data.get('experience') else 'не указано',
            'area': data.get('area', {}).get('name') if data.get('area') else 'не указано'
        }
    else:
        print(f"Ошибка {response.status_code}")
        return None
    
