# whatsphish
whatsapp phishing using selenium  

for ssl certificates
openssl genrsa -out key.pem 2048
openssl req -new -x509 -key key.pem -out cert.pem -days 365

Enter the test.csv of the information of the people to be social engineered, the results will be written to the result.csv file. In case of any crash, there is no need to start from 0, you can continue sending messages from the last person sent.
