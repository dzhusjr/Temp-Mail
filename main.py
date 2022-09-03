import pyperclip,requests,random,string,time,sys,re,os
from colorama import init, Fore
init()

API = 'https://www.1secmail.com/api/v1/'
domain = random.choice(['1secmail.com', '1secmail.net', '1secmail.org'])
directory = os.path.join(os.getcwd(), r'temp_mail/All Mails')
length = 0
saving = False

def generateUserName():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

def extract():
    return [re.search(r'login=(.*)&', newMail)[1], re.search(r'domain=(.*)', newMail)[1]]

def print_statusline(msg: str):
    last_msg_length = len(print_statusline.last_msg) if hasattr(print_statusline, 'last_msg') else 0
    print(' ' * last_msg_length, end='\r')
    print(msg, end='\r')
    sys.stdout.flush()
    print_statusline.last_msg = msg

def find_url(text):
    return [x[0] for x in re.findall(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",text)]

def deleteMail():
    data = {
        'action': 'deleteMailbox',
        'login': f'{extract()[0]}',
        'domain': f'{extract()[1]}'
    }
    print_statusline(f"Disposing your email address - {mail}" + '\n')
    requests.post('https://www.1secmail.com/mailbox', data=data)

def checkMails():  # sourcery skip: avoid-builtin-shadow
    global length
    req = requests.get(f'{API}?action=getMessages&login={extract()[0]}&domain={extract()[1]}').json()
    if len(req) > length:
        length = len(req)
        idList = [i['id'] for i in req]
        if not os.path.exists(directory):
            os.makedirs(directory)
        id = idList[0]
        req = requests.get(f'{API}?action=readMessage&login={extract()[0]}&domain={extract()[1]}&id={id}').json()
        sender = req['from']
        subject = req['subject']
        date = req['date']
        content = req['textBody']
        print_statusline(f"You received {length} {'mails' if length > 1 else 'mail'}.\nLinks:\n" + ''.join([Fore.BLUE+link+Fore.WHITE+'\n' for link in find_url(content)]) if find_url(content) else 'No links found.\n')
        if saving:
            mail_file_path = os.path.join(directory, f'{subject or "no_subj"}_{id}.txt')
            with open(mail_file_path,'w') as file:
                file.write(f"Sender: {sender}" + '\n' + "To: " + mail + '\n' + "Subject: " + subject + '\n' + "Date: " + date + '\n' + "Content: " + content + '\n')

    if length == 0:
        print_statusline("Your mailbox is empty.")
try:
    newMail = f"{API}?login={generateUserName()}&domain={domain}"
    mail = f"{extract()[0]}@{extract()[1]}"
    pyperclip.copy(mail)
    print(f"\nYour temporary email is {Fore.GREEN+mail+Fore.WHITE} (Email address copied to clipboard.)\n------------------------------------ | Inbox | ------------------------------------\n")
    while 1:
        checkMails()
        time.sleep(3)

except(KeyboardInterrupt):
    deleteMail()
    print("\nProgramme Interrupted")
    os.system('cls' if os.name == 'nt' else 'clear')
