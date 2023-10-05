import json, csv
from haralyzer import HarParser, HarPage

def main():
    with open('lehoublon.com.har', 'r') as f:
        har_parser = HarParser(json.loads(f.read()))

    print(har_parser.pages)

    output = []
    for entry in har_parser.har_data['entries']:
        output.append({
            'root_domain': '.'.join(entry['request']['url'].split('/')[2].split('.')[-2:]),
            'url': entry['request']['url']
        })

    output = sorted(output, key=lambda k: k['root_domain'])
    with open('output.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['root_domain', 'url'])
        for row in output:
            writer.writerow([row['root_domain'], row['url']])


if __name__ == '__main__':
    main()