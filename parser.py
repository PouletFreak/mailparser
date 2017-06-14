import email, json, os, re
import magic
import ssdeep
import hashlib
import datetime


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sha1(fname):
    hash_sha1 = hashlib.sha1()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()

def sha256(fname):
    hash_sha256 = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def sha512(fname):
    hash_sha512 = hashlib.sha512()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha512.update(chunk)
    return hash_sha512.hexdigest()

def main():

    file = '31a891f9e074c81b4688ac5b9faac9c1e3786a20'
    f = open(file, 'r')


    msg = email.message_from_file(f)
    message_json = {}

    message_json['parsedate'] = str(datetime.datetime.now())
    message_json['filename'] = file
    message_json['md5'] = md5(file)
    message_json['sha1'] = sha1(file)
    message_json['sha512'] = sha512(file)
    message_json['sha256'] = sha256(file)

    detach_dir = './' + message_json['filename'][0:10]

    if not os.path.exists(detach_dir):
        os.makedirs(detach_dir)

    scan_json = {}
    scan_json['Date'] = msg['Date']
    scan_json['From'] = msg['From']
    scan_json['Subject'] = msg['Subject']
    scan_json['To'] = msg['To']
    scan_json['Cc'] = msg['Cc']
    scan_json['Bcc'] = msg['Bcc']
    scan_json['References'] = msg['References']
    scan_json['body'] = ''
    scan_json['body_html'] = ''
    scan_json['xml'] = ''
    scan_json['email_addresses'] = []
    scan_json['ip_addresses'] = []
    scan_json['attachments'] = []
    message_json['scan'] = scan_json

    attachment = {}

    for part in msg.walk():

        application_pattern = re.compile('application/*')
        image_pattern = re.compile('image/*')
        audio_pattern = re.compile('audio/*')
        video_pattern = re.compile('video/*')
        content_type = part.get_content_type()

        if content_type == 'text/plain':

            ''' Fills the main email part into the JSON Object and searches for valid email and ip addresses '''

            mainpart = part.get_payload()
            scan_json['body'] += mainpart
            mail_matches = re.findall(r'[\w\.-]+@[\w\.-]+', mainpart) #finds mail addresses in text
            for match in mail_matches:
                if match not in scan_json['email_addresses']:
                    scan_json['email_addresses'].append(match)

            ip_matches = re.findall( r'[0-9]+(?:\.[0-9]+){3}', mainpart) #Finds IP Addresses in text
            for match in ip_matches:
                scan_json['ip_addresses'].append(match)

        if content_type == 'text/html':
            scan_json['body_html'] += part.get_payload()

        if content_type == 'text/xml':
            scan_json['xml'] += part.get_payload()

        if re.match(image_pattern, content_type) \
                or re.match(application_pattern, content_type) \
                or re.match(audio_pattern, content_type) \
                or re.match(video_pattern, content_type):

            filename = part.get_filename()
            counter = 1

            if not filename:
                filename = 'part-%03d%s' % (counter, 'bin')
                counter += 1

            att_path = os.path.join(detach_dir, filename)
            print att_path
            attachment['filepath'] = att_path   #TODO: zum kaufen bekommen
            attachment['filename'] = filename
            attachment['Type'] = content_type


            if not os.path.isfile(att_path):
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

            attachment['size'] = os.path.getsize(att_path)
            attachment['magic'] = magic.from_file(att_path, mime=True)
            try:
                attachment['ssdeep'] = ssdeep.hash_from_file(att_path)
            except:
                pass
            attachment['md5'] = md5(att_path)
            attachment['sha1'] = sha1(att_path)
            attachment['sha512'] = sha512(att_path)
            attachment['sha256'] = sha256(att_path)

            scan_json['attachments'].append(attachment)
            attachment = {}

    try:
        json_data = json.dumps(message_json, indent=4, sort_keys=True)
    except UnicodeDecodeError:
        json_data = json.dumps(message_json, indent=4, sort_keys=True, ensure_ascii=False)

    print json_data

if __name__ == '__main__':
    main()