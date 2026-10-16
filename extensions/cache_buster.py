import hashlib

# Translated via ChatGPT from
# https://distresssignal.org/busting-css-cache-with-jekyll-md5-hash


def file_version(path):
    md5 = hashlib.md5()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            md5.update(block)
    return f"v={md5.hexdigest()[:10]}"


def bust_file_cache(file_name):
    if '://' in file_name:
        return file_name
    return f"{file_name}?{file_version(f'content/{file_name}')}"


def theme_asset_filter(relative_url):
    def theme_asset(path):
        return relative_url(f"theme/{path}?{file_version(f'theme/static/{path}')}")
    return theme_asset
