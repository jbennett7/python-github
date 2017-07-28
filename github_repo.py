import requests
import json
import yaml
import re

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

LABELS_KEY_LIS = [
    ('name', str),
    ('color', str, 6)]


class GithubRepository(object):
    def __init__(self, token, organization, name):
        self._header = {'Authorization': 'token {}'.format(token)}
        self._organization = organization
        self._name = name
        check = requests.get(GITHUB_URL, headers=self._header).status_code
        assert check == 200, "Github access error html status code: {}".format(check)
        self._url = '{}/repos/{}/{}'.format(GITHUB_URL, self._organization, self._name)
        result = requests.get(self._url, headers=self._header)
        if result.status_code == 404:
            self.exists = False
            self._configuration = dict(name=self._name)
        elif result.status_code == 200:
            self.exists = True
            self._configuration = dict((k, result.json()[k]) for k in [i for i, o in CONFIGURABLE_KEY_LIST])
            self._labels = requests.get(re.sub('{/name}', '', result.json()['labels_url']), headers=self._header).json()
        else:
            raise Exception("Unkown Error, status code: {}".format(result.status_code))

    def create_repository(self):
        assert self._configuration, "Repository, {}, has no configuration.".format(self._name)
        # Does the repository already exist?
        try:
            result = requests.get(self._url, headers=self._header)
            assert result.status_code == 200
        except AssertionError:
            # If not try to create it using the value in self._organization as an organization name.
            try:
                result = requests.post(
                    '{}/orgs/{}/repos'.format(GITHUB_URL, self._organization),
                    data=json.dumps(self._configuration),
                    headers=self._header)
                assert result.status_code == 201
            except AssertionError:
                # If self._organization name is not an organization name then maybe it is a user name.
                try:
                    result = requests.post(
                        '{}/user/repos'.format(GITHUB_URL),
                        data=json.dumps(self._configuration),
                        headers=self._header)
                    assert result.status_code == 201
                except AssertionError:
                    raise Exception("HTML Status code: {}".format(result.status_code))
        self._repository = result.json()
        return result.status_code

    def set_configuration(self, configuration):
        assert isinstance(configuration, dict), "Configuration is not a dictionary"
        for key in configuration:
            assert key in [k[0] for k in CONFIGURABLE_KEY_LIST], "key {} does not exist in {}".format(key, CONFIGURABLE_KEY_LIST)
            assert isinstance(configuration[key], [o for k, o in CONFIGURABLE_KEY_LIST if k == key][0]), "Data in configuration is malformed: {}".format(configuration)
            self._configuration[key] = configuration[key]
        result = requests.post(self._url, headers=self._header, data=json.dumps(self._configuration))
        return result.status_code

    def get_configuration(self):
        assert self._configuration, "Repository, {}, has no configuration.".format(self._name)
        return self._configuration

    def get_labels(self):
        try:
            return self._labels
        except Exception:
            try:
                result = requests.get(self._url, headers=self._header)
                if result.status_code != 200:
                    raise Exception, "Repository, (), does not exist".format(self._name)
                labels_url = re.sub('{/name}', '', result.json()['labels_url'])
                result = requests.get(labels_url, headers=header)
                self._labels = result.json()
            except Exception:
                raise
        return self._labels

    def add_label(self, label):
        result = requests.get(self._url, headers=self._header)
        labels_url = re.sub('{/name}', '', result.json()['labels_url'])
        result = requests.post(labels_url,data=json.dumps(label), headers=header)
        return result.status_code

    def set_labels(self, label_list):
        assert self._labels, "Repository, {}, has no labels.".format(self._name)
        created_labels = []
        deleted_labels = []
        modified_labels = []
        try:
            result = requests.get(self._url, headers=self._header)
            labels_url = re.sub('{/name}', '', result.json()['labels_url'])
            result = requests.get(labels_url, headers=self._header)
            old_labels = result.json()
            for label in list(old_labels):
                if label['name'] not in [l['name'] for l in label_list]:
                    deleted_labels.append(label['name'])
                    result = requests.delete(label['url'], headers=self._header)
                    old_labels.remove(label)
                    if result.status_code != 204:
                        raise Exception("Error deleting label: {}, status code: {}".format(label['name'], result.status_code))
            for label in old_labels:
                for nlabel in label_list:
                    if label['name'] == nlabel['name']:
                        if label['color'] != nlabel['color']:
                            result = requests.post(label['url'],data=json.dumps(nlabel),headers=self._header)
                            modified_labels.append(label)
                            if result.status_code != 200:
                                raise Exception("Error modifying label {}, status code: {}".format(label, result.status_code))
            for label in label_list:
                if label['name'] in [l['name'] for l in old_labels]:
                    continue
                result = requests.post(labels_url, data=json.dumps(label), headers=self._header)
                created_labels.append(label)
        except Exception:
            raise
        return created_labels, deleted_labels, modified_labels

