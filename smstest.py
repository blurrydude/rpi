from twilio.rest import Client 
 
account_sid = 'AC26cbcaf937e606af51c6a384728a4e75' 
auth_token = '7b8e7b5be6d3e4c2246d9f8ed5156ddc' 
client = Client(account_sid, auth_token) 
 
message = client.messages.create(  
                              messaging_service_sid='MG1cf18075f26dc8ff965a5d2d1940dab5', 
                              body='This is a test',      
                              to='+19377166465' 
                          ) 
 
print(message.sid)