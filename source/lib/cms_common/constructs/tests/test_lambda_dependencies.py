# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# Standard Library
from os.path import abspath, dirname

# Third Party Libraries
from syrupy.types import SerializableData

# AWS Libraries
from aws_cdk import assertions


def test_lambda_dependencies_snapshot(
    empty_lambda_dependencies_stack: assertions.Template,
    snapshot_json_with_matcher: SerializableData,
) -> None:

    assert empty_lambda_dependencies_stack.to_json() == snapshot_json_with_matcher


def test_requiremments_file_correctly_populated(
    populated_lambda_dependencies_stack: assertions.Template,
) -> None:
    with open(
        f"{dirname(abspath(__file__))}/mock_dependency_layer/populated/requirements.txt",
        "r",
        encoding="utf-8",
    ) as req_file:
        generated_requirements = set(req_file.read().splitlines())

    expected_requirements = set(
        [
            "-i https://pypi.org/simple",
            "./../../../../../../lib",
            "attrs==25.3.0",
            "aws-lambda-powertools[tracer,validation]==3.15.1",
            "aws-xray-sdk==2.14.0",
            "botocore==1.38.44",
            "cattrs==25.1.1",
            "certifi==2025.6.15",
            "cffi==1.17.1",
            "charset-normalizer==3.4.2",
            "cryptography==45.0.4",
            "fastjsonschema==2.21.1",
            "idna==3.10",
            "jmespath==1.0.1",
            "pycparser==2.22",
            "pyjwt[crypto]==2.10.1",
            "python-dateutil==2.9.0.post0",
            "requests==2.32.4",
            "six==1.17.0",
            "toml==0.10.2",
            "typing-extensions==4.14.0",
            "urllib3==2.5.0",
            "wrapt==1.17.2",
        ]
    )

    assert generated_requirements == expected_requirements
