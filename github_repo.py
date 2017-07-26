import requests
import json
import yaml

GITHUB_URL = 'https://api.github.com'

CONFIGURABLE_KEY_LIST = [
    ('name', str),
    ('description', str),
    ('private', bool),
    ('has_issues', bool),
    ('has_projects', bool),
    ('has_wiki', bool),
    ('homepage', str),
    ('allow_squash_merge', bool),
    ('allow_merge_commit', bool),
    ('allow_rebase_merge', bool)]


class GithubRepository(object):
    def __init__(self, token, organization, name):
        self._header = {'Authorization': 'token {}'.format(token)}
        self._organization = organization
        self._name = name
        check = requests.get(GITHUB_URL, headers=self._header).status_code
        assert check == 200, "Github access error html status code: {}".format(check)
        self._url = '{}/repos/{}/{}'.format(GITHUB_URL, self._organization, self._name)
        result = requests.get(self._url, self._header)
        if result.status_code == 404:
            self.exists = False
        elif result.status_code == 200:
            self.exists = True
            self._repository = result.json()

    def create_repository(self):
        assert self._configuration, "Repository, {}, has no configuration.".format(self._name)
        try:
            result = requests.get(self._url, headers=self._header)
            assert result.status_code == 200
        except AssertionError:
            try:
                result = requests.post('{}/orgs/{}/repos'.format(GITHUB_URL, self._organization), data=json.dumps(self._configuration), headers=self._header)
                assert result.status_code == 201
            except AssertionError:
                try:
                    result = requests.post('{}/user/repos'.format(GITHUB_URL), data=json.dumps(self._configuration), headers=self._header)
                    assert result.status_code == 201
                except AssertionError:
                    raise
        self._repository = result.json()

    def set_configuration(self, configuration):
        assert isinstance(configuration, dict)
        assert len(configuration.keys()) == len(CONFIGURABLE_KEY_LIST)
        for key in configuration:
            assert key in [k[0] for k in CONFIGURABLE_KEY_LIST], "key {} does not exist in {}".format(key, CONFIGURABLE_KEY_LIST)
            assert isinstance(configuration[key], [o for k, o in CONFIGURABLE_KEY_LIST if k == key][0])
        self._configuration = configuration

    def get_configuration(self):
        assert self._configuration, "Repository, {}, has no configuration.".format(self._name)
        return self._configuration
