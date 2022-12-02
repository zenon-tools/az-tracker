import json
import datetime
import sys
import os
import re

from utils.node_rpc_wrapper import NodeRpcWrapper
from utils.telegram_wrapper import TelegramWrapper


def check_and_send_az_phase_events(cached_phases, new_phases, new_projects):
    telegram = globals()['telegram']
    channel_id = globals()['cfg']['telegram_channel_id']

    # Check for new Phases. Assume Phase is new if the id was not present in the cached data.
    for id in new_phases:
        if id not in cached_phases and len(new_phases) > len(cached_phases):
            m = create_new_phase_message(
                new_phases[id], new_projects[new_phases[id]['projectId']])
            if 'error' in m:
                handle_error(m['error'])
            else:
                r = telegram.bot_send_message_to_chat(channel_id, m['message'])
                print(
                    f'Phase submitted message sent to Telegram: {r.status_code}')

    # Check for status updates.
    for id in new_phases:
        if id in cached_phases and new_phases[id]['status'] != cached_phases[id]['status']:
            m = create_phase_update_message(
                new_phases[id], new_projects[new_phases[id]['projectId']])
            if 'error' in m:
                handle_error(m['error'])
            else:
                r = telegram.bot_send_message_to_chat(channel_id, m['message'])
                print(
                    f'Phase update message sent to Telegram: {r.status_code}')


def check_and_send_az_project_events(cached_projects, new_projects):
    telegram = globals()['telegram']
    channel_id = globals()['cfg']['telegram_channel_id']

    # Check for new Projects. Assume Project is new if the id was not present in the cached data.
    for id in new_projects:
        if id not in cached_projects and len(new_projects) > len(cached_projects):
            m = create_new_project_message(new_projects[id])
            if 'error' in m:
                handle_error(m['error'])
            else:
                r = telegram.bot_send_message_to_chat(channel_id, m['message'])
                print(
                    f'Project submitted message sent to Telegram: {r.status_code}')

    # Check for status updates.
    for id in new_projects:
        if id in cached_projects and new_projects[id]['status'] != cached_projects[id]['status']:
            m = create_project_update_message(new_projects[id])
            if 'error' in m:
                handle_error(m['error'])
            else:
                r = telegram.bot_send_message_to_chat(channel_id, m['message'])
                print(
                    f'Project update message sent to Telegram: {r.status_code}')


def create_new_phase_message(phase_data, project_data):
    try:
        m = '<b>New phase submitted</b>\n\n'
        m = m + '<b>Phase</b>\n' + escape_chars(phase_data['name']) + '\n\n'
        m = m + '<b>Project</b>\n' + escape_chars(project_data['name']) + '\n\n'
        m = m + '<b>Description</b>\n' + escape_chars(phase_data['description']) + '\n\n'
        m = m + '<b>Funding requested</b>\n' + (str(int(phase_data['znnFundsNeeded'] / 100000000))) + ' ZNN' + \
            ' + ' + \
                (str(int(phase_data['qsrFundsNeeded'] /
                 100000000))) + ' QSR\n\n'
        m = m + phase_data['url']
        return {'message': m}
    except KeyError:
        return {'error': 'KeyError: create_new_phase_message'}


def create_phase_update_message(phase_data, project_data):
    try:
        m = '<b>Phase status updated</b>\n\n'
        m = m + '<b>Phase</b>\n' + escape_chars(phase_data['name']) + '\n\n'
        m = m + '<b>Project</b>\n' + escape_chars(project_data['name']) + '\n\n'
        m = m + '<b>New status</b>\n' + get_az_state(phase_data['status'])

        if phase_data['status'] in [1, 2, 3]:
            m = m + '\n\n<b>Votes</b>\n'
            yes_no_votes = phase_data['votes']['yes'] + \
                phase_data['votes']['no']
            m = m + 'Yes ' + str(phase_data['votes']['yes']) + ' | No ' + str(phase_data['votes']['no']) + \
                ' | Abstain ' + \
                    str(phase_data['votes']['total'] - yes_no_votes) + '\n'

        return {'message': m}
    except KeyError:
        return {'error': 'KeyError: create_phase_update_message'}


def create_new_project_message(project_data):
    try:
        m = '<b>New project submitted</b>\n\n'
        m = m + '<b>Project</b>\n' + escape_chars(project_data['name']) + '\n\n'
        m = m + '<b>Description</b>\n' + escape_chars(project_data['description']) + '\n\n'
        m = m + '<b>Funding requested</b>\n' + (str(int(project_data['znnFundsNeeded'] / 100000000))) + ' ZNN' + \
            ' + ' + \
                (str(
                    int(project_data['qsrFundsNeeded'] / 100000000))) + ' QSR\n\n'
        m = m + project_data['url']
        return {'message': m}
    except KeyError:
        return {'error': 'KeyError: create_new_project_message'}


def create_project_update_message(project_data):
    try:
        m = '<b>Project status updated</b>\n\n'
        m = m + '<b>Project</b>\n' + escape_chars(project_data['name']) + '\n\n'
        m = m + '<b>New status</b>\n' + get_az_state(project_data['status'])

        if project_data['status'] in [1, 2, 3]:
            m = m + '\n\n<b>Votes</b>\n'
            yes_no_votes = project_data['votes']['yes'] + \
                project_data['votes']['no']
            m = m + 'Yes ' + str(project_data['votes']['yes']) + ' | No ' + str(project_data['votes']['no']) + \
                ' | Abstain ' + \
                    str(project_data['votes']['total'] - yes_no_votes) + '\n'

        return {'message': m}
    except KeyError:
        return {'error': 'KeyError: create_project_update_message'}


def get_az_state(state):
    if state == 0:
        return 'Voting \U0001F5F3'
    elif state == 1:
        return 'Accepted \U00002705'
    elif state == 2:
        return 'Funded \U00002705'
    elif state == 3:
        return 'Not accepted \U0000274c'
    elif state == 4:
        return 'Completed \U00002705'


def escape_chars(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s


def read_file(file_path):
    f = open(file_path)
    content = json.load(f)
    f.close()
    return content


def write_to_file_as_json(data, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def handle_error(message):
    telegram = globals()['telegram']
    dev_chat_id = globals()['cfg']['telegram_dev_chat_id']

    print(message)

    # Send the developer a message if a developer chat ID is configured
    if len(dev_chat_id) != 0:
        telegram.bot_send_message_to_chat(chat_id=dev_chat_id, message=message)

    # Exit script on error
    sys.exit()


def main():
    global cfg
    global telegram

    # Get current file path
    path = os.path.dirname(os.path.abspath(__file__))

    # Read config
    cfg = read_file(f'{path}/config/config.json')

    # Data store directory
    DATA_STORE_DIR = f'{path}/data_store'

    # Node status file
    NODE_STATUS_FILE = f'{DATA_STORE_DIR}/node_status_data.json'

    # A-Z cache file
    AZ_CACHE_FILE = f'{DATA_STORE_DIR}/az_data.json'

    # Check and create data store directory
    if not os.path.exists(DATA_STORE_DIR):
        os.makedirs(DATA_STORE_DIR, exist_ok=True)

    # Check and create node status file
    if not os.path.exists(NODE_STATUS_FILE):
        write_to_file_as_json({'height': 0, 'error': False}, NODE_STATUS_FILE)

    # Check and create A-Z cache file
    if not os.path.exists(AZ_CACHE_FILE):
        open(AZ_CACHE_FILE, 'w+').close()

    # Create wrappers
    node = NodeRpcWrapper(node_url=cfg['node_url_http'])
    telegram = TelegramWrapper(
        bot_api_key=cfg['telegram_bot_api_key'])

    # Get latest momentum
    latest_momentum = node.get_latest_momentum()
    if 'error' in latest_momentum:
        handle_error(latest_momentum['error'])

    node_status = read_file(NODE_STATUS_FILE)

    # Check node status
    if latest_momentum['height'] > node_status['height'] and not node_status['error']:
        write_to_file_as_json(
            {'height': latest_momentum['height'], 'error': False}, NODE_STATUS_FILE)
    else:
        write_to_file_as_json(
            {'height': latest_momentum['height'], 'error': True}, NODE_STATUS_FILE)
        handle_error('Node is stuck. Running prevented.')

    # Get latest A-Z projects
    az_projects = node.get_all_az_projects()
    if 'error' in az_projects:
        handle_error(az_projects['error'])

    # Get latest A-Z phases
    az_phases = node.get_all_az_phases()
    if 'error' in az_phases:
        handle_error(az_phases['error'])

    new_az_data = {'projects': az_projects, 'phases': az_phases, 'timestamp': str(
                datetime.datetime.now())}

    new_az_data = read_file(f'{DATA_STORE_DIR}/fake_az.json')

    # Get cached A-Z data from file
    if os.stat(AZ_CACHE_FILE).st_size != 0:
        cached_az_data = read_file(AZ_CACHE_FILE)
    else:
        cached_az_data = None

    # Cache current A-Z data to file
    write_to_file_as_json(new_az_data, AZ_CACHE_FILE)

    # Check for new Phase and Project events if cached data exists
    if cached_az_data is not None:
        check_and_send_az_phase_events(
            cached_az_data['phases'], new_az_data['phases'], new_az_data['projects'])
        check_and_send_az_project_events(
            cached_az_data['projects'], new_az_data['projects'])


if __name__ == '__main__':
    print(f'{str(datetime.datetime.now())}: Starting')
    main()
    print(f'{str(datetime.datetime.now())}: Completed')
