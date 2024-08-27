# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# Standard Library
import os
from typing import Dict, Generator
from unittest.mock import patch

# Third Party Libraries
import pytest
from moto import mock_aws

# AWS Libraries
import boto3


@pytest.fixture(name="mocked_module_env_vars_values", scope="session")
def fixture_mocked_module_env_vars_values() -> Dict[str, str]:
    return {
        "APPLICATION_TYPE": "test-application-type",
        "SOLUTION_ID": "test-solution-id",
        "SOLUTION_NAME": "test-solution-name",
        "SOLUTION_VERSION": "v0.0.0",
        "S3_ASSET_BUCKET_BASE_NAME": "test-bucket-name",
        "S3_ASSET_KEY_PREFIX": "test-key-prefix",
        "USER_AGENT_STRING": "test-user-agent-string",
    }


@pytest.fixture(scope="session", autouse=True)
def fixture_mock_dynamo_env_vars(
    mocked_module_env_vars_values: Dict[str, str]
) -> Generator[None, None, None]:
    env_vars = os.environ.copy()
    env_vars.update(mocked_module_env_vars_values)
    with patch.dict(os.environ, env_vars):
        yield


@pytest.fixture(name="dynamodb_table")
def fixture_dynamodb_table() -> Generator[str, None, None]:
    with mock_aws():
        table_name = "test_table"
        table = boto3.resource("dynamodb")
        table.create_table(
            AttributeDefinitions=[
                {
                    "AttributeName": "id",
                    "AttributeType": "S",
                },
            ],
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        table.Table(table_name).put_item(
            Item={
                "id": "test_id_1",
                "test_val": "test_val_1",
            }
        )
        table.Table(table_name).put_item(
            Item={
                "id": "test_id_2",
                "test_val": "test_val_2",
            }
        )
        yield table_name
