from config.constants import SIZE_CODE_MAP, CATEGORY_ID_MAP

def get_size_codes(sizes):
    return [SIZE_CODE_MAP.get(size) for size in sizes if SIZE_CODE_MAP.get(size)]

def get_category_id(category_name):
    return CATEGORY_ID_MAP.get(category_name)
