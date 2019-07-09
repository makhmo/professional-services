# !/usr/bin/env python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Demonstrates how to perform basic access management with Google Cloud IAM.

For more information, see the documentation at
https://cloud.google.com/iam/docs/granting-changing-revoking-access.
"""

import os

import googleapiclient.discovery
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
    scopes=['https://www.googleapis.com/auth/cloud-platform'])
service = googleapiclient.discovery.build(
    'cloudresourcemanager', 'v1', credentials=credentials)


# [START iam_get_policy]
def get_policy(project_id):
    """Gets IAM policy for a project."""

    # pylint: disable=no-member
    policy = service.projects().getIamPolicy(resource=project_id, body={}).execute()
    # print(policy)
    return policy
# [END iam_get_policy]


# [START iam_modify_policy_add_member]
def modify_policy_add_member(policy, role, member):
    """Adds a new member to a role binding."""
    binding = next(b for b in policy['bindings'] if b['role'] == role)
    binding['members'].append(member)
    # print(binding)
    return policy
# [END iam_modify_policy_add_member]


# [START iam_modify_policy_add_role]
def modify_policy_add_role(policy, role, member):
    """Adds a new role binding to a policy."""
    binding = {
        'role': role,
        'members': [member]
    }
    policy['bindings'].append(binding)
    # print(policy)
    return policy
# [END iam_modify_policy_add_role]


# [START iam_set_policy]
def set_policy(project_id, policy):
    """Sets IAM policy for a project."""

    # pylint: disable=no-member
    policy = service.projects().setIamPolicy(
        resource=project_id, body={
            'policy': policy
        }).execute()
    # print(policy)
    return policy
# [END iam_set_policy]


