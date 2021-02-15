import requests
import os

import config

class Pearson:

    def __init__(self, username: str, password: str, client_id: str):
        self.session = requests.Session()

        self.username = username
        self.password = password
        self.client_id = client_id

        self.access_token = None

    def _auth(self):
        response = self.session.post(
            url = 'https://login.pearson.com/v1/piapi/login/webcredentials',
            data = {
                'username': self.username,
                'password': self.password,
                'client_id': self.client_id,
                'isMobile': True,
                'grant_type': 'password',
            })

        self.access_token = response.json()['data']['access_token']

        response = self.session.get(
            url = 'https://etext.pearson.com/api/nextext-api/v1/api/nextext/eps/authtoken',
            headers = {
                'isSanvan': 'false',
                'X-Authorization': self.access_token,
            })

    def _bookshelf(self):
        return self.session.get(
            url = 'https://stpaperapi.prd-prsn.com/etext/v2/courseboot/convergedreader/compositeBookShelf/',
            headers = {
                'X-Authorization': self.access_token,
                'isMobile': 'true',
                'isDeeplink': 'true',
                'includeRegistrar': 'true',
                'User-Agent': 'okhttp/4.4.0',
            }).json()

    def _download(self, book):
        os.system("curl -L -X $'GET' -H $'Accept-Encoding: gzip, deflate' -H $'Connection: close' -H $'etext-cdn-token: {}' -H $'User-Agent: okhttp/4.4.0' $'{}' --output /tmp/foobar.gz".format(
            self.session.cookies.get_dict()['etext-cdn-token'][1:-1],
            book['uPdfUrl'],
        ))
        os.system('gzip -d -f /tmp/foobar.gz')
        os.system('mv /tmp/foobar ./{}'.format(os.path.basename(book['uPdfUrl'])))

        """
        response = self.session.get(
            url = 'https://etext.pearson.com/eps/pearson-reader/cecff624-083e-4be2-bc20-48513ecd9e9c/etext1updfs/CM76647197_uPDF.pdf',
            headers = {
                'etext-cdn-token': self.session.cookies.get_dict()['etext-cdn-token'][1:-1],
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'close',
                'User-Agent': 'okhttp/4.4.0',
            })

        data = response.content
        with open('output.pdf', 'wb') as f:
            f.write(data)
        """

p = Pearson(
    username = config.username,
    password = config.password,
    client_id = config.client_id,
)

p._auth()
books = p._bookshelf()
for i, book in enumerate(books['entries']):
    if os.path.exists('./{}'.format(os.path.basename(book['uPdfUrl']))):
        print('\033[0;32m[{}] {}\033[0m'.format(i, book['title'].strip()))
    else:
        print('\033[0;31m[{}] {}\033[0m'.format(i, book['title'].strip()))

n = input('> ')
p._download(books['entries'][int(n)])
