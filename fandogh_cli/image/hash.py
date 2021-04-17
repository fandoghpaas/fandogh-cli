import mmh3


def hash_file(path):
    return mmh3.hash(open(path, 'rb').read(), signed=False)

