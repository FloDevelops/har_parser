import json, csv, yaml, re
from os import listdir
from haralyzer import HarParser


config = yaml.load(open('config.yml', 'r'), Loader=yaml.FullLoader)
config_requests = config.get('requests')

folders = {
    'input': 'input_files_har',
    'output': 'output_files_csv'
}



def main():
    records = list()
    for file in listdir(folders.get('input')):
        if file == '.DS_Store' or file == '.gitkeep':
            continue
        with open(folders.get('input') + '/' + file, 'r') as f:
            records.extend(parse_har(f))

    write_to_csv(records, 'all.csv')



def parse_har(file):
    har_parser = HarParser(json.loads(file.read()))

    output = []
    for entry in har_parser.har_data.get('entries'):
        initiator = entry.get('_initiator')
        intiator_url = initiator.get('url')
        if intiator_url is None and initiator.get('stack') is not None:
            if initiator.get('stack').get('callFrames') is not None and len(initiator.get('stack').get('callFrames')) > 0:
                intiator_url = initiator.get('stack').get('callFrames')[0].get('url')
            elif initiator.get('stack').get('parent').get('callFrames') is not None and len(initiator.get('stack').get('parent').get('callFrames')) > 0:
                intiator_url = initiator.get('stack').get('parent').get('callFrames')[0].get('url')

        record = dict(
            request_status = entry.get('response').get('status'),
            request_url = entry.get('request').get('url'),
            request_initiator_type = initiator.get('type'),
            request_initiator_url = intiator_url,
            page_url = find_page(har_parser, entry.get('pageref', None))
        )
        record['request_root_domain'] = '.'.join(record.get('request_url').split('/')[2].split('.')[-2:]) if record.get('request_url') is not None else None
        record['request_domain'] = record.get('request_url').split('/')[2] if record.get('request_url') is not None else None
        record['request_path_level_1'] = record.get('request_url').split('/')[3].split('?')[0] if record.get('request_url') is not None and len(record.get('request_url').split('/')) > 3 else None
        record['request_path_level_2'] = record.get('request_url').split('/')[4].split('?')[0] if record.get('request_url') is not None and len(record.get('request_url').split('/')) > 4 else None
        record['request_path_level_3'] = record.get('request_url').split('/')[5].split('?')[0] if record.get('request_url') is not None and len(record.get('request_url').split('/')) > 5 else None
        record['request_path_full'] = '/'.join(record.get('request_url').split('/')[3:]).split('?')[0] if record.get('request_url') is not None else None
        record['request_params'] = record.get('request_url').split('?')[1] if record.get('request_url') is not None and len(record.get('request_url').split('?')) > 1 else None

        if record.get('request_root_domain') is not None:
            record['request_risk'] = '1-high'
            for domain_pattern in config_requests.get('low_risk').get('domain_patterns'):
                if re.search(domain_pattern, record.get('request_root_domain')):
                    record['request_risk'] = '3-low'
                    break
            for url_pattern in config_requests.get('low_risk').get('url_patterns'):
                if re.search(url_pattern, record.get('request_url')):
                    record['request_risk'] = '3-low'
                    break

            for pattern in config_requests.get('medium_risk').get('domain_patterns'):
                if re.search(pattern, record.get('request_root_domain')):
                    record['request_risk'] = '2-medium'
                    break
            for pattern in config_requests.get('high_risk').get('domain_patterns'):
                if re.search(pattern, record.get('request_root_domain')):
                    record['request_risk'] = '1-high'
                    break

        else:
            record['request_risk'] = 'high'


        record['request_initiator_domain'] = record.get('request_initiator_url').split('/')[2] if record.get('request_initiator_url') is not None and  len(record.get('request_initiator_url').split('/')) > 2 else None
        record['page_domain'] = record.get('page_url').split('/')[2] if record.get('page_url') is not None else None

        record = reorder_keys(record, [
            'request_risk',
            'request_status',
            'request_root_domain',
            'request_domain',
            'request_path_level_1',
            'request_path_level_2',
            'request_path_level_3',
            'request_path_full',
            'request_params',
            'request_url',
            'request_initiator_domain',
            'request_initiator_url',
            'request_initiator_type',
            'page_domain',
            'page_url'
            ])

        output.append(record)

    return output


def find_page(har_parser, page_name):
    for page in har_parser.har_data.get('pages'):
        if page.get('id') == page_name:
            return page.get('title', None)
    return None

def reorder_keys(record, order):
    record = {k: record[k] for k in order if k in record}
    return record

def write_to_csv(output, file_name):
    output = sorted(output, key=lambda k: (k.get('request_root_domain'), k.get('request_url'), '' if k.get('page') is None else k.get('page')))

    filtered_output = [record.get('request_url')[:100] for record in output if record.get('request_risk') == '1-high']
    print(json.dumps(filtered_output, indent=2))

    with open(folders.get('output') + '/' + '.'.join(file_name.split('/')[-1].split('.')[:-1]) + '.csv', 'w') as csvfile:
        fieldnames = list(output[1000].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for row in output:
            writer.writerow(row)



if __name__ == '__main__':
    main()