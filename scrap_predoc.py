from bs4 import BeautifulSoup
import requests
import re
import time
import smtplib
from datetime import datetime
import os

email = os.environ.get('EMAIL')
email_pass = os.environ.get('EMAIL_PASS')


def find_not_at_nber():
    html_text = requests.get('https://www.nber.org/career-resources/research-assistant-positions-not-nber').text
    soup = BeautifulSoup(html_text, 'lxml')
    jobs = soup.find_all('p')[1:-2]

    for job in jobs:
        try:
            link = job.find('a').get('href').rstrip('\n')
        except AttributeError:
            pass
        job = job.text.replace('\xa0', ' ')
        try:
            sponsoring_researcher = re.findall('Sponsoring.*: (.*)', job)[0].strip()
            field = re.findall('Field.*: (.*)', job)[0].strip()
            institution = re.findall('Institution:\\s+(.*)', job)[0].strip()
        except IndexError:
            pass

        with open('jobs/predoc.txt', 'a') as file:
            file.write(f"{sponsoring_researcher} \n {field} \n {institution} \n {link} \n \n ")


if not os.path.exists('jobs/predoc.txt'):
    with open('jobs/predoc.txt', 'w') as first_time:
        first_time.write(' ')

if __name__ == '__main__':
    while True:
        with open('jobs/predoc.txt', 'r') as old_file:
            old_job_line = old_file.readline().strip()
        open('jobs/predoc.txt', 'w').close()

        find_not_at_nber()

        with open('jobs/predoc.txt', 'r') as new_file:
            new_job = new_file.read()
            new_job_line = re.match('(.*)', new_job).group(0).strip()

        if new_job_line != old_job_line:
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()

                smtp.login(email, email_pass)

                subject = 'Check Out New Job'
                body = re.findall('(.*?) \\n \\n', new_job, flags=re.DOTALL)
                body = '\n \n'.join(body[0:3])

                msg = f'Subject: {subject}\n\n{body}'

                smtp.sendmail(email, email, msg)
                print('Check mailbox')
                break
        else:
            time_wait = 60
            print(f'''Nothing new at {datetime.now(tz=None)}...
            Waiting {time_wait} minutes...''')
            time.sleep(time_wait * 60)
