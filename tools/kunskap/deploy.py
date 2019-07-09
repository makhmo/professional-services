from google.cloud import bigquery_datatransfer
from google.protobuf.struct_pb2 import Struct
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

import access
import config


def run_deploy():
    client = bigquery_datatransfer.DataTransferServiceClient()

    project_id = config.config_vars['output_project_id']

    # Get the full path to your project.
    parent = client.project_path(project_id)

    params = Struct()
    sql = open(config.config_vars['sql_file_path'], 'r').read()
    params["query"] = sql.format(**config.config_vars)
    params["write_disposition"] = "WRITE_APPEND"
    params["destination_table_name_template"] = config.config_vars['output_table_name']

    transfer_config = {
        "destination_dataset_id": config.config_vars['output_dataset_id'],
        "display_name": config.config_vars['display_name'],
        "data_source_id": "scheduled_query",
        'schedule': config.config_vars['schedule'],
        "params": params,
    }

    parent = parent + "/locations/us"

    found_cfg = False
    for cfg in client.list_transfer_configs(parent):
        if config.config_vars['display_name'] == cfg.display_name:
            found_cfg = True

    if not found_cfg:
        response = client.create_transfer_config(parent, transfer_config)
        print(response)


def update_service_account():
    credentials = GoogleCredentials.get_application_default()

    service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

    project_id = config.config_vars['output_project_id']
    request = service.projects().list(filter='projectId=' + project_id)
    response = request.execute()
    project_info = response.get('projects', [])[0]

    service_account = 'serviceAccount:service-{projectNumber}@gcp-sa-bigquerydatatransfer.iam.gserviceaccount.com'.format(
        **project_info)

    policy = access.get_policy(project_id)
    service_account_token_minter_role = 'roles/iam.serviceAccountShortTermTokenMinter'

    found_role = False
    for role in policy['bindings']:
        if role['role'] == service_account_token_minter_role:
            if service_account in role['members']:
                found_role = True

    if not found_role:
        policy = access.modify_policy_add_role(policy, service_account_token_minter_role, service_account)
        print('modified_policy:' + str(policy))
        access.set_policy(project_id, policy)


if __name__ == '__main__':
    update_service_account()
    run_deploy()
