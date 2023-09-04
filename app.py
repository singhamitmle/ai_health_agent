from flask import Flask, request, session, jsonify
from twilio.twiml.voice_response import Gather, VoiceResponse
from twilio.rest import Client
import random
from deepgram import Deepgram
import requests
import logging
import sys

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

app.secret_key = '0909t$8f92AC5b7835ef6484dfc0c099bb81f644tEP$#0'

# Replace with your Twilio credentials
TWILIO_ACCOUNT_SID = 'XXXXXXXXXXXX111111111111111111'
TWILIO_AUTH_TOKEN = 'YYYYYYYYYYYYYY11111111111111111'

# Replace with your Deepgram API key
DEEPGRAM_API_KEY = '00000000000000000ZZZZZZZZZZZZZZ'

def transcribe_audio(audio_url):
    headers = {
        'Authorization': f'Bearer {DEEPGRAM_API_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        'url': audio_url,
    }

    response = requests.post('https://api.deepgram.com/v1/listen', headers=headers, json=data)

    if response.status_code == 200:
        transcription = response.json().get('transcription')
        return transcription
    else:
        return None

@app.route('/voice', methods=['POST'])
def voice():
    app.logger.info("Received POST request to /voice")
    response = VoiceResponse()

    with Gather(input='speech', action='/handle-patient-name', method='POST', speechTimeout='auto') as gather:
        gather.say("Welcome to Assort Health. Please say your first and last name.")

    response.append(gather)

    return str(response)

@app.route('/handle-patient-name', methods=['POST'])
def handle_patient_name():
    app.logger.info("Received POST request to /handle-voice")
    response = VoiceResponse()

    name_result = request.form.get('SpeechResult')
    app.logger.info(name_result)

    if name_result:
        session['patient_name'] = name_result
        app.logger.info(f"name : {name_result}")
        response.say("Thank you. Please provide your payer's name and ID.")
        gather = Gather(input='speech', action='/handle-insurance-info', method='POST', speechTimeout='auto')
        response.append(gather)
        
    else:
        app.logger.warning("No speech result data found in the response.")
        response.say("Sorry, we couldn't understand your response. Please try again.")

    return str(response)

@app.route('/handle-insurance-info', methods=['POST'])
def handle_insurance_info():
    response = VoiceResponse()
    insurance_result = request.form.get('SpeechResult')

    if insurance_result:
        session['insurance_result'] = insurance_result
        app.logger.info(f"insurance details : {insurance_result}")
        response.say("Thank you for providing your insurance information.")

        gather = Gather(input='speech', action='/handle-referral', method='POST', speechTimeout='auto')
        gather.say("Do you have a referral? Please say 'yes' or 'no'.")
        response.append(gather)

    else:
        response.say("Sorry, we couldn't understand your response. Please try again.")
    return str(response)

@app.route('/handle-referral', methods=['POST'])
def handle_referral():
    response = VoiceResponse()
    referral_result = request.form.get('SpeechResult')
    app.logger.info(f"referral_result : {referral_result}")
    if referral_result:
        if referral_result.lower() == 'yes.':
            
            gather = Gather(input='speech', action='/handle-referrer-name', method='POST', speechTimeout='auto')
            gather.say("Please provide the name of the referrer.")
            response.append(gather)
        elif referral_result.lower() == 'no.':
            gather = Gather(input='speech', action='/handle-medical-complaint', method='POST', speechTimeout='auto')
            gather.say("Please describe the reason for your visit.")
            response.append(gather)

            
        else:
            response.say("Sorry, we couldn't understand your response. Please try again.")
    return str(response)

@app.route('/handle-referrer-name', methods=['POST'])
def handle_referrer_name():
    response = VoiceResponse()
    referrer_name = request.form.get('SpeechResult')
    app.logger.info(f"referrer_name : {referrer_name}")
    if referrer_name:
        session['referrer_name'] = referrer_name
        response.say("Thank you for providing the name of the referrer.")
        gather = Gather(input='speech', action='/handle-medical-complaint', method='POST', speechTimeout='auto')
        gather.say("Please tell us the reason you are calling in today.")
        response.append(gather)

        
    else:
        response.say("Sorry, we couldn't understand your response. Please try again.")
    return str(response)


@app.route('/handle-medical-complaint', methods=['POST'])
def handle_medical_complaint():
    response = VoiceResponse()
    medical_complaint = request.form.get('SpeechResult')

    if medical_complaint:
        session['medical_complaint'] = medical_complaint
        app.logger.info(f"Medical Complaint: {medical_complaint}")
        response.say("Thank you for providing your medical complaint.")
        gather = Gather(input='speech', action='/handle-address', method='POST', speechTimeout='auto')
        gather.say("Please provide your address.")
        response.append(gather)
        
    else:
        response.say("Sorry, we couldn't understand your response. Please try again.")

    return str(response)

@app.route('/handle-address', methods=['POST'])
def handle_address():
    response = VoiceResponse()
    address = request.form.get('SpeechResult')

    if address:
        session['address'] = address
        app.logger.info(f"Address: {address}")
        response.say("Thank you for providing your address.")
        gather = Gather(input='speech', action='/handle-contact-info', method='POST', speechTimeout='auto')
        gather.say("Please provide your contact information.")
        response.append(gather)

    else:
        response.say("Sorry, we couldn't understand your response. Please try again.")

    return str(response)

@app.route('/handle-contact-info', methods=['POST'])
def handle_contact_info():
    response = VoiceResponse()
    contact_info = request.form.get('SpeechResult')

    if contact_info:
        session['contact_info'] = contact_info
        app.logger.info(f"Contact Information: {contact_info}")
        response.say("Thank you for providing your contact information.")
        
        
    else:
        response.say("Sorry, we couldn't understand your response. Please try again.")

    return handle_provider_availability()



@app.route('/handle-provider-availability', methods=['POST'])
def handle_provider_availability():
    response = VoiceResponse()

    # Generate fake provider and appointment data
    providers = [
        {"name": "Dr. Smith", "specialty": "Internal Medicine", "location": "123 Main St."},
        {"name": "Dr. Johnson", "specialty": "Pediatrics", "location": "456 Elm St."},
        {"name": "Dr. Brown", "specialty": "Dermatology", "location": "789 Oak St."}
    ]

    available_times = [
        "9:00 AM", "10:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"
    ]

    # Randomly select a provider and time slot
    selected_provider = random.choice(providers)
    selected_time = random.choice(available_times)

    response.say(f"Thank you for using Assort Health. We have found an available appointment with {selected_provider['name']} in {selected_provider['location']} on {selected_time}.")
    
    
    session['selected_provider'] = selected_provider
    session['selected_time'] = selected_time
    #send_appointment_sms()
    print("Session Contents:", session)
    return str(response)


def send_sms(to_phone_number, body):
    
    twilio_account_sid = TWILIO_ACCOUNT_SID
    twilio_auth_token = TWILIO_AUTH_TOKEN

    client = Client(twilio_account_sid, twilio_auth_token)

    from_phone_number = '+18777933904'  

    # Send the SMS message
    message = client.messages.create(
        body=body,
        from_=from_phone_number,
        to=to_phone_number
    )

    return message.sid



def send_appointment_sms():
    
    selected_provider = session.get('selected_provider', 'N/A')
    selected_time = session.get('selected_time', 'N/A')

    caller_phone_number = request.form.get('From', 'N/A')
    sms_body = f"Thank you for using Assort Health. Your appointment is scheduled with {selected_provider} on {selected_time}. We look forward to seeing you."

    send_sms(caller_phone_number, sms_body)



@app.route('/end-call', methods=['POST'])
def end_call():
    send_appointment_sms()
    return str(VoiceResponse())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=8080, debug=True)
