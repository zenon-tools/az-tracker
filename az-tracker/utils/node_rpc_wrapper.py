import json
import datetime
from utils.http_wrapper import HttpWrapper


class NodeRpcWrapper(object):

    def __init__(self, node_url):
        self.node_url = node_url

    def get_latest_momentum(self):
        r = self.__ledger_get_frontier_momentum()
        if r.status_code == 200:
            d = json.loads(r.text)
            try:
                return {'height': d['result']['height'], 'timestamp': str(datetime.datetime.now())}
            except KeyError:
                return {'error': 'KeyError: get_latest_momentum'}
        else:
            return {'error': f'Bad response: get_latest_momentum {r.status_code}'}

    def get_all_az_projects(self):
        r = self.__embedded_az_get_all()
        if r.status_code == 200:
            d = json.loads(r.text)
            projects = {}
            try:
                for project in d['result']['list']:
                    projects[project['id']] = {'name': project['name'], 'description': project['description'], 'url': project['url'], 'znnFundsNeeded': project['znnFundsNeeded'],
                                               'qsrFundsNeeded': project['qsrFundsNeeded'], 'status': project['status'], 'votes': {'yes': project['votes']['yes'],
                                                                                                                                   'no': project['votes']['no'], 'total': project['votes']['total']}}
            except KeyError:
                return {'error': 'KeyError: get_all_az_projects'}
            return projects
        else:
            return {'error': f'Bad response: get_all_az_projects {r.status_code}'}

    def get_all_az_phases(self):
        r = self.__embedded_az_get_all()
        if r.status_code == 200:
            d = json.loads(r.text)
            phases = {}
            try:
                for project in d['result']['list']:
                    for phase in project['phases']:
                        phases[phase['phase']['id']] = {'projectId': phase['phase']['projectID'], 'name': phase['phase']['name'], 'description': phase['phase']['description'], 'url': phase['phase']['url'], 'znnFundsNeeded': phase['phase']['znnFundsNeeded'],
                                                        'qsrFundsNeeded': phase['phase']['qsrFundsNeeded'], 'status': phase['phase']['status'], 'votes': {'yes': phase['votes']['yes'],
                                                                                                                                                          'no': phase['votes']['no'], 'total': phase['votes']['total']}}
            except KeyError:
                return {'error': 'KeyError: get_all_az_phases'}
            return phases
        else:
            return {'error': f'Bad response: get_all_az_phases {r.status_code}'}

    def __ledger_get_frontier_momentum(self):
        return HttpWrapper.post(self.node_url, {'jsonrpc': '2.0', 'id': 1,
                                                'method': 'ledger.getFrontierMomentum', 'params': []})

    def __embedded_az_get_all(self, params=[0, 1000]):
        return HttpWrapper.post(self.node_url, {'jsonrpc': '2.0', 'id': 1,
                                                'method': 'embedded.accelerator.getAll', 'params': params})
