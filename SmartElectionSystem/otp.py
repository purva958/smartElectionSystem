import random
from twilio.rest import Client

def generate_otp():
    return random.randint(100000, 999999)

def send_otp(mobile_number, voterid):
    
    account_sid = 'AC398781fc1258fb9856fcec452a5ef520' 
    auth_token = '07d26bb893a5d5311c832534a9eff788'    
    twilio_phone_number = '+15305085793 '  
    
    client = Client(account_sid, auth_token)

    message = f"Your VoterID is {voterid}. It is valid for 10 minutes."

    try:
        message = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=mobile_number
        )
        print(f"VoterID sent successfully to {mobile_number}")
    except Exception as e:
        print(f"Failed to send OTP: {e}")

def otp_verification(user_otp, generated_otp):
    if user_otp == generated_otp:
        return "VoterID verified successfully!"
    else:
        return "Invalid OTP. Please try again."

if __name__ == "__main__":
    mobile_number = input("Enter your mobile number (with country code): ")
    
    voterid = generate_otp()
    
    send_otp(mobile_number, voterid)
    
    user_otp = int(input("Enter the VoterID you received: "))
    

    verification_status = otp_verification(user_otp, voterid)
    print(verification_status)