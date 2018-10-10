import requests


def gencheck(url):
    if not url.endswith('/rss.xml'):
        return {"type": "error", "data": "This is not a random web proxy."}
    r = requests.get(url)
    patterns = [b'<generator>https://getnikola.com/</generator>',         # v7.6.1
                b'<generator>http://getnikola.com/</generator>',          # v7.0.0
                b'<generator>Nikola <http://getnikola.com/></generator>', # v6.3.0
                b'<generator>nikola</generator>']                         # v6.2.1
    result = -1
    for i, p in enumerate(patterns):
        if p in r.content:
            result = i

    if r.status_code != 200:
        return {"type": "error", "data": 'HTTP Error {0}.'.format(r.status_code)}
    else:
        return {"type": "result", "data": result}


if __name__ == '__main__':
    print(gencheck(input("URL: "))["data"])
