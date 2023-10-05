import json, csv
from os import listdir
from haralyzer import HarParser, HarPage

folders = {
    'input': 'input_files_har',
    'output': 'output_files_csv'
}



def main():
    for file in listdir(folders['input']):
        if file == '.DS_Store' or file == '.gitkeep':
            continue
        with open(folders['input'] + '/' + file, 'r') as f:
            parse_har(f)



def parse_har(file):
    har_parser = HarParser(json.loads(file.read()))

    output = []
    for entry in har_parser.har_data['entries']:
        record = {
            'request_root_domain': '.'.join(entry['request']['url'].split('/')[2].split('.')[-2:]),
            'request_status': entry['response']['status'],
            'request_url': entry['request']['url'],
            'page': find_page(har_parser, entry.get('pageref', None))
        }
        output.append(record)
    write_to_csv(output, file.name)



def find_page(har_parser, page_name):
    for page in har_parser.har_data['pages']:
        if page['id'] == page_name:
            return page.get('title', None)
    return None



def write_to_csv(output, file_name):
    output = sorted(output, key=lambda k: (k['request_root_domain'], k['request_url'], '' if k['page'] is None else k['page']))
    with open(folders['output'] + '/' + '.'.join(file_name.split('/')[-1].split('.')[:-1]) + '.csv', 'w') as csvfile:
        fieldnames = ['request_root_domain', 'request_status', 'request_url', 'page']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in output:
            writer.writerow(row)



if __name__ == '__main__':
    main()