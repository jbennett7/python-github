import requests
import json

GITHUB_URL = 'https://api.github.com'

class GithubRepository(object):
    def __init__(self, token, organization, name):
        self._header = {'Authorization': 'token {}'.format(token)}
        self._organization = organization
        self._name = name
        self._repo_url = '{}/repos/{}/{}'.format(
            GITHUB_URL, self._organization, self._name)
        self._labels_url = '{}/repos/{}/{}/labels'.format(
            GITHUB_URL, self._organization, self._name)
        try:
            check = requests.get(GITHUB_URL, headers=self._header).status_code
            assert check == 200
        except AssertionError:
            raise Exception(
                'Github access error status code: {}'.format(check))
        self.create_repository(dict(name=self._name))

    def does_exist(self):
        try:
            result = requests.get(self._repo_url, headers=self._header)
            assert result.status_code == 200
            return True
        except AssertionError:
            return False

    def create_repository(self, configuration):
        if not self.does_exist():
            try:
                result = requests.post(
                    self._repo_url,
                    data=json.dumps(configuration),
                    headers=self._header)
                assert result.status_code == 201
            except AssertionError:
                try:
                    result = requests.post(
                        self._repo_url,
                        data=json.dumps(configuration),
                        headers=self._header)
                    assert result.status_code == 201
                except AssertionError:
                    raise Exception(
                        'Cannot create repository: {} status code: {}'.format(
                            result.status_code))

    def _label_url(label_name):
        return '{}/{}'.format(self._labels_url, label_name)

    def set_configuration(self, configuration):
        assert isinstance(configuration, dict)
        try:
            result = requests.patch(
                self._repo_url,
                headers=self._header,
                data=json.dumps(configuration))
            assert result.status_code == 200
        except AssertionError:
            raise Exception(
                'Unable to set configurations: {}, for repository: {}, status code: {}'.format(
                    configuration,
                    self._name,
                    result.status_code))
        return result.status_code

    def get_configuration(self):
        try:
            result = requests.get(
                self._repo_url,
                headers=self._header)
            assert result.status_code == 200
        except AssertionError:
            raise Exception(
                'Unable to retrieve the configuration of repository: {}, status code: {}'.format(
                    self._name,
                    result.status_code))
        return result.json()

    def get_labels(self):
        try:
            result = requests.get(
                self._labels_url,
                headers=self._header)
            assert result.status_code == 200
        except AssertionError:
            raise Exception(
                'Unable to retrieve labels for repository: {}, status code: {}'.format(
                    self._name,
                    result.status_code))
        return result.json()

    def compare_label(self, label):
        assert isinstance(label, dict)
        try:
            result = requests.get(
                self._label_url(label['name']),
                headers=self._header)
            assert result.status_code == 200
            if label['name'] == result.json()['name'] and \
               label['color'] == result.json()['color']:
                return True
            else:
                return False
        except AssertionError:
            return False

    def create_label(self, label):
        assert isinstance(label, dict)
        try:
            result = requests.post(
                    self._labels_url,
                data=json.dumps(label),
                headers=self._header)
            assert result.status_code == 201
        except AssertionError:
            raise Exception(
                'Unable to create label: {}, for repository: {}, status code: {}'.format(
                    label['name'],
                    self._name,
                    result.status_code))
        return result.status_code

    def modify_label(self, label):
        assert isinstance(label, dict)
        try:
            result = requests.patch(
                self._label_url(label['name']),
                data=json.dumps(label),
                headers=self._header)
            assert result.status_code == 200
        except AssertionError:
            raise Exception(
                'Unable to modify label: {}, for repository: {}, status code: {}'.format(
                    label['name'],
                    self._name,
                    result.status_code))
        return result.status_code

    def delete_label(self, label_name):
        try:
            result = requests.delete(
                self._label_url(label['name']),
                headers=self._header)
            assert result.status_code == 204
        except AssertionError:
            raise Exception(
                'Unable to delete label: {}, from repository: {}, status code: {}'.format(
                    label_name,
                    self._name,
                    result.status_code))
        return result.status_code
