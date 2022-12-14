#  Copyright 2016-2021, Pulumi Corporation.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import List, Optional, Union


from pulumi.output import Output
from pulumi.provider import ConstructResult
import pulumi.provider as provider

import aws_iam
from aws_iam.iam import Role, Policy, PolicyStatement


class Provider(provider.Provider):
    def __init__(self) -> None:
        super().__init__(aws_iam.__version__, aws_iam.__schema__)

    def construct(
        self,
        name: str,
        resource_type: Optional[str] = None,
        env: Optional[str] = "",
        policy_statements: Optional[Union[List[PolicyStatement], Output]] = None,
        assume_role_policy: Optional[str] = None,
        managed_policy_arns: Optional[List[str]] = None,
        max_session_duration: Optional[int] = None,
        name_is_prefix: Optional[bool] = True,
        description: Optional[str] = None,
        name_suffix: Optional[str] = None,
    ) -> ConstructResult:
        if resource_type == 'aws_iam:index:Role':
            return _construct_role(name, env, policy_statements, assume_role_policy, managed_policy_arns, max_session_duration, name_is_prefix)
        elif resource_type == 'aws_iam:index:Policy':
            return _construct_policy(name, policy_statements, description, name_suffix)
        raise Exception(f'Unknown resource type {resource_type}')


def _construct_role(
        name: str,
        env: Optional[str] = "",
        policy_statements: Optional[Union[List[PolicyStatement], Output]] = None,
        assume_role_policy: Optional[str] = None,
        managed_policy_arns: Optional[List[str]] = None,
        max_session_duration: Optional[int] = None,
        name_is_prefix: Optional[bool] = True,
) -> ConstructResult:

    # Create the component resource.
    role = Role(name, env, policy_statements, assume_role_policy, managed_policy_arns, max_session_duration, name_is_prefix)

    # Return the component resource's URN and outputs as its state.
    return provider.ConstructResult(
        urn=role.urn,
        state={
            'role': role.role,
        })

def _construct_policy(
        name: str,
        policy_statements: List[PolicyStatement],
        description: Optional[str] = None,
        name_suffix: Optional[str] = None,
) -> ConstructResult:

    # Create the component resource.
    policy = Policy(name, policy_statements, description, name_suffix)

    # Return the component resource's URN and outputs as its state.
    return provider.ConstructResult(
        urn=policy.urn,
        state={
            'policy': policy.policy,
        })
