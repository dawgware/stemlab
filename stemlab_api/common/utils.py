import urllib

def hasitems(collection):
    if isinstance(collection, dict) or isinstance(collection, list):
        return collection is not None and len(collection) > 0
    return False


def append_to_url(root_url, url):
    if root_url[-1] == '/' and url[0] == '/':
        url = url.lstrip('/')
    return "{root}{url}".format(root=root_url, url=url)

def create_url_with_params(base_url, parameters):
    params = None
    if isinstance(parameters, dict):
        print "DICT: ", len(parameters), parameters
        if len(parameters) > 1:
            return "{url}?{params}".format(url=base_url, params=urllib.urlencode(parameters))
        else:
            param = parameters.items()[0]
            return "{url}?{param}={val}".format(url=base_url, param=param[0], val=param[1])
