import requests
from fandogh_cli import VERSION, NAME


class Version:
    def __init__(self, version_str):
        self.version_tuple = self._parse_version(version_str)
        pass

    def _parse_version(self, version_str):
        try:
            version = list(map(int, version_str.split('.')))
            if len(version) == 0:
                return [0, ]
            version.extend([0] * (3 - len(version)))
            return version
        except Exception:
            return [0]

    def __len__(self):
        return len(self.version_tuple)

    def __gt__(self, other):

        this, that = self._make_same_length(self.version_tuple, other.version_tuple)
        for index, version_part in enumerate(this):
            if version_part > that[index]:
                return True
            elif version_part < that[index]:
                return False
        return False

    def _make_same_length(self, first, second):
        max_length = max(len(first), len(second))
        the_first = first + [0] * (max_length - len(first))
        the_second = second + [0] * (max_length - len(second))
        return the_first, the_second

    def compare(self, other):
        assert isinstance(other, Version)
        this, that = self._make_same_length(self.version_tuple, other.version_tuple)
        for index, version in enumerate(this):
            if version > that[index]:
                return index + 1
            elif version < that[index]:
                return -1 * (index + 1)
        return 0

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return not self > other

    def __lt__(self, other):
        if self > other or self == other:
            return False
        return True

    def __eq__(self, other):
        assert isinstance(other, Version)
        this, that = self._make_same_length(self.version_tuple, other.version_tuple)
        return this == that

    def __str__(self):
        return ".".join(map(str, self.version_tuple))

    def __repr__(self):
        return str(self)


def get_package_info():
    url = "https://pypi.org/pypi/{}/json".format(NAME)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        raise RuntimeError("Unexpected response status while calling pypi")
    except Exception as exp:
        raise RuntimeError("Unable to connect to pypi.org: {}".format(exp))


def get_latest_version():
    package_info = get_package_info()
    try:
        return Version(package_info['info']['version'])
    except KeyError as missing_key:
        raise RuntimeError("Unexpected response: {} is missing from response".format(missing_key))


def get_current_version():
    return Version(VERSION)

