from collections import OrderedDict
from collection_json import Collection
from influxdb.resultset import ResultSet
from stemlab_api.common.db_utils import TEMPERATURE, HUMIDITY

def create_links(rel, url):
    return {'rel': rel, 'href': url}


def create_template(version, href, data_args):
    collection = OrderedDict()
    collection['version'] = version
    collection['href'] = href
    template_data = []
    for key, value in data_args.items():
        data_dict = {'name': key,
                     'value': value,
                     'prompt': ''}
        template_data.append(data_dict)
    collection['template'] = {'data': template_data}
    return {'collection': collection}


def create_data_item(item):
    if 'data' not in item:
        # raise ValueError("Not data values found in item dictionary")
        item_data = item
    else:
        item_data = item['data']

    item_dict = OrderedDict()
    item_dict['href'] = item_data['url']
    if 'links' not in item:
        item_dict['links'] = []
    else:
        item_dict['links'] = item['links']
    data_list = []
    for key, value in item_data.items():
        data_dict = {}
        if 'url' != key:
            data_dict['name'] = key
            data_dict['value'] = value
            data_dict['prompt'] = ""
            data_list.append(data_dict)

    item_dict['data'] = data_list
    return item_dict


def create_collection(version, href, items, links=None):
    collection = OrderedDict()
    collection['version'] = version
    collection['href'] = href
    collection['links'] = links
    collection_items = []
    if items is not None:
        if isinstance(items, dict):
            single_item = create_data_item(items)
            collection_items.append(single_item)
        elif isinstance(items, list):
            for item in items:
                single_item = create_data_item(item)
                collection_items.append(single_item)
        elif isinstance(items, ResultSet):
            print "Yup, its a ResultSet"
    collection['items'] = collection_items
    return {'collection': collection}

