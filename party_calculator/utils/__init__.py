import importlib


def create_object(module_name, model_name, **kwargs):
    cls = class_for_name(module_name, model_name)
    # obj = cls(**kwargs) # for tests
    cls.objects.create(**kwargs)


def class_for_name(module_name, class_name):
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cls


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_nested_json_value(json_dict, key):
    for dict_key in json_dict:
        if dict_key == key:
            return json_dict[dict_key]

        if isinstance(dict_key, dict):
            search_result = get_nested_json_value(dict_key, key)
            if search_result:
                return search_result

