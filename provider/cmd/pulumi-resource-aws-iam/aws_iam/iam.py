"""Manages IAM roles and policies."""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import pulumi
from pulumi import log
from pulumi.output import Output
from pulumi_aws.iam import Policy
from pulumi_aws.iam.role import Role
from pulumi_aws.iam.role_policy import RolePolicy

import aws_iam
from aws_iam.util import get_hash


@dataclass
class PolicyStatement(pulumi.ComponentResource):
    """
    Represents an IAM Policy statement which grants (or denies) `actions` on `resources`.

    Resource ARNs and Actions can be wildcarded. To see what Actions are available for a service, see
    https://docs.aws.amazon.com/service-authorization/latest/reference/reference_policies_actions-resources-contextkeys.html
    """

    actions: List[str]
    resources: List[str] = field(default_factory=lambda: ["*"])
    sid: str = None
    effect: str = "Allow"
    conditions: str = None

    @property
    def name(self):
        """Returns a Policy's sid."""
        if self.sid:
            return self.sid

        # i definitely keep putting strs these fields by accident...
        for val in [self.actions, self.resources]:
            if not isinstance(val, list):
                raise ValueError(f"Found {type(val)}, expected List[str]. Value: {val}")

        return get_hash("".join(self.actions + self.resources))

    def to_dict(self):
        """Returns a dictionary of a Policy Statement object's values."""
        log.debug(f"PolicyStatement.to_dict: {self.actions} and {self.resources}")
        d = {
            # if you get a TypeError at this point, ensure your ARNs coming from outputs are acquired through an apply()
            # eg: `ecr.arn.apply(create_build_role_policy_json)` (see deployment.py:117)
            "Sid": self.name,
            "Effect": self.effect,
            "Action": self.actions,
            "Resource": self.resources,
        }
        if self.conditions:
            d["Condition"] = json.loads(self.conditions)

        return d


class Role(pulumi.ComponentResource):
    role: Role

    def __init__(
        self,
        name: str,
        env: Optional[str] = "",
        policy_statements: Optional[Union[List[PolicyStatement], Output]] = None,
        assume_role_policy: Optional[str] = None,
        managed_policy_arns: Optional[List[str]] = None,
        max_session_duration: Optional[int] = None,
        name_is_prefix: Optional[bool] = True,
    ) -> None:

        super().__init__(
            "aws_iam:index:Role",
            name,
            env,
            policy_statements,
            assume_role_policy,
            managed_policy_arns,
            max_session_duration,
            name_is_prefix,
        )

        """Creates a role with standardized naming and optionally an inline policy."""
        name_arg = "name_prefix" if name_is_prefix else "name"
        role_args = {name_arg: name, "path": f"/{env}/" if env else "/"}
        if assume_role_policy:
            role_args["assume_role_policy"] = assume_role_policy
        if managed_policy_arns:
            role_args["managed_policy_arns"] = managed_policy_arns
        if max_session_duration:
            role_args["max_session_duration"] = max_session_duration

        role = Role(f"{name}", **role_args)

        # policy statements likely have pulumi Output data in them
        policy = None
        if isinstance(policy_statements, Output):
            policy = policy_statements.apply(
                lambda statements: self._format_role_policy(statements)
            )
        elif isinstance(policy_statements, list):
            policy = self._format_role_policy(policy_statements)
        elif policy_statements:
            log.error(
                "Unable to create role policy, the value provided for policy statements was an unrecognized type."
            )

        if policy:
            RolePolicy(
                f"{name}-policy",
                role=role.id,
                policy=policy,
            )
        self.role = role
        self.register_outputs({"role": role})

    def _format_role_policy(policy_statements: List[PolicyStatement]) -> str:
        """Converts PolicyStatements into digestible JSON."""
        return json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [stmt.to_dict() for stmt in policy_statements],
            }
        )


class Policy(pulumi.ComponentResource):
    policy: Policy

    def __init__(
        self,
        name: str,
        policy_statements: List[PolicyStatement],
        description: Optional[str] = None,
        name_suffix: Optional[str] = None,
    ) -> None:

        super().__init__(
            "aws_iam:index:Policy",
            name,
            policy_statements,
            description,
            name_suffix,
        )
        """
        Creates an IAM policy. If no name suffix is provided, randomness will be used in its place.

        *NOTE*: IAM policies are limited to 6,144 or 10,240 characters depending on where it is used.
        """
        if not name:
            raise ValueError("Name must be provided.")

        if not name_suffix:
            name_suffix = get_hash(
                "".join([policy.name for policy in policy_statements])
            )

        name = f"{name}-{name_suffix}"

        statements = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [policy.to_dict() for policy in policy_statements],
            }
        )

        policy = Policy(
            name,
            name=name,
            description=description,
            policy=statements,
        )

        self.policy = policy
        self.register_outputs({"policy": policy})


def get_policy_arns(policies: List[Union[Policy, str]]) -> List[str]:
    """Returns the ARNs of the passed list of Policies"""
    if not policies:
        return None
    return [p.arn if isinstance(p, Policy) else p for p in policies]
