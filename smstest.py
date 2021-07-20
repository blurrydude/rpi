from twilio.rest import Client 
 
account_sid = '' 
auth_token = '' 
client = Client(account_sid, auth_token) 
 
message = client.messages.create(  
                              messaging_service_sid='', 
                              body='This is a test',      
                              to='+19377166465' 
                          ) 
 
print(message.sid)