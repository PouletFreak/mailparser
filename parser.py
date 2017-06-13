import email, json, os, re

def main():
    f = open('cb76bf63e8abfa5b152808a8a2a6396ce2d070c7.eml', 'r')

    detach_dir = '.'
    msg = email.message_from_file(f)
    message_json = {};
    message_json['From'] = msg['From']
    message_json['Subject'] = msg['Subject']
    message_json['To'] = msg['To']
    message_json['Cc'] = msg['Cc']
    message_json['References'] = msg['References']
    message_json['Body Text'] = ''
    message_json['Body Html'] = ''
    message_json['EMail Addresses'] = []
    message_json['IP Addresses'] = []



    json_data = json.dumps(message_json)
    #print json_data


    for part in msg.walk():

        #print part.get_content_type()
        application_pattern = re.compile('application/*')
        image_pattern = re.compile('image/*')
        type = part.get_content_type()

        if type == 'text/plain':

            '''Fills the main email part into the JSON Object and searches for valid email and ip addresses'''

            mainpart = part.get_payload()
            message_json['Body Text'] += mainpart
            mail_matches = re.findall(r'[\w\.-]+@[\w\.-]+', mainpart) #finds mail addresses in text
            for match in mail_matches:
                if match not in message_json['EMail Addresses']:
                    message_json['EMail Addresses'].append(match)

            ip_matches = re.findall( r'[0-9]+(?:\.[0-9]+){3}', mainpart) #Finds IP Addresses in text
            for match in ip_matches:
                message_json['IP Addresses'].append(match)




        if type == 'text/html':
            message_json['Body Html'] += part.get_payload()

        if  re.match(image_pattern,type) or re.match(application_pattern,type):
            filename = part.get_filename()
            counter = 1
            #print type
            if not filename:
                filename = 'part-%03d%s' % (counter, 'bin')
                counter += 1

            att_path = os.path.join(detach_dir, filename)

            if not os.path.isfile(att_path):
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

    json_data = json.dumps(message_json,indent=4, sort_keys=False)
    print json_data

if __name__ == '__main__':
    main()