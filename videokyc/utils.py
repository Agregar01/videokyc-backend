from datetime import datetime
import requests
from background_task import background
from videokyc.models import ImageComparison

def get_request_data(request, instance):
    get_user_request_details(request, instance)


@background(schedule=2)
def get_extra_request_details(instance_id):
    instance = ImageComparison.objects.filter(id=instance_id).first()
    print("inside here")
    mock_sim_swap(instance)
    smile_ofac_aml(instance)


def mock_sim_swap(instance):
    swap = {
        "phone": instance.phone,
        "network": "MTN",
        "swap_detected": False,
        "owner": f"{instance.firstname} {instance.othernames or ''} {instance.lastname}",
        "sim_date": datetime.now()
    }
    instance.sim_swap_details = swap
    instance.save()

def get_user_request_details(request, instance):
        print("inside the request")
        host = request.get_host()
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown User-Agent')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        instance.device_info = {"host": host, "user_agent": user_agent, "ip": ip}
        instance.save()


def convert_adversemedia_str(adverseMedia):
    result = ""
    for adverse in adverseMedia:
        title = adverse['title']
        sourceLink = adverse['sourceLink']
        publisher = adverse['publisher']
        datePublished = adverse['datePublished']
        result = f"{result} title: {title}, source link: {sourceLink}, publisher: {publisher}, date published: {datePublished};"

    return result

def convert_sanction_str(sanctions):
    result = ""
    for sanc in sanctions:
        dateOfBirth = sanc['dateOfBirth']
        nationality = sanc['nationality']
        listed_date = sanc['sourceDetails']['listed_date']
        source_name = sanc['sourceDetails']['source_name']
        source_type = sanc['sourceDetails']['source_type']
        source_link =  ", ".join(sanc['sourceDetails']['source_link'])
        result = f"Nationality: {nationality}, Date of Birth: {dateOfBirth}, Listed Date: {listed_date}, Source Name: {source_name}, Source Type: {source_type}, Source Link: {source_link};"

    return result

def smile_ofac_aml(instance):

    username = 'user'
    password = 'user'

    url = 'http://165.22.70.167:9100/apicore/v1/verifications/aml'
    
    payload = {
        'country': "Ghana",
        'fullname': f"{instance.firstname} {instance.othernames or ''} {instance.lastname}",
        'dateOfBirth': instance.date_of_birth,
        'clientDetails': {
            'clientId': 10,
            'userId': 7,
            'signature': '',
            'timestamp': '',
            'callbackUrl': ''
        }
    }

    response = requests.post(url, json=payload, auth=(username, password))
    print(response.text)
    if response.status_code == 200:
        data = response.json()
        if data['success'] == True:
            result = data['amlVerificationDetails']
            if result == None or result is None:
                return {
                    'success': True,
                    'match': False,
                    'error': False,
                    'aml': None,
                    'sanctions_list': None
                } 
            persons_found = result['amlDetails']['nofPersonsFound']

            if(len(persons_found) > 0):
                adverse_media = ""
                sanctions_list = ""
                people = result['amlDetails']['people']
                for item in people:
                    print(item)
                    admeida_str = convert_adversemedia_str(item['adverseMedia'])
                    dobs = item['datesOfBirth']
                    dobs = ", ".join(dobs)
                    adverse_media = f"{item['name']}; date of births: {dobs}"
                    adverse_media = f"{adverse_media} {admeida_str}"

                for item in people:
                    admeida_str = convert_sanction_str(item['sanctions'])
                    dobs = item['datesOfBirth']
                    dobs = ", ".join(dobs)
                    sanctions_list = f"{item['name']}; date of births: {dobs}"
                    sanctions_list = f"{sanctions_list} {admeida_str}"

                ofac = {
                    'success': True,
                    'match': True,
                    'error': False,
                    'aml': adverse_media,
                    'sanctions_list': sanctions_list
                }
            else:
                ofac = {
                    'success': True,
                    'match': False,
                    'error': False
                }
        else:
            ofac = {
                'success': False,
                'match': False,
                'error': True
            }
    else:
        ofac = {
            'success': False,
            'match': False,
            'error': True
        }
    instance.ofac_verification = ofac
    instance.save()
    print(ofac)