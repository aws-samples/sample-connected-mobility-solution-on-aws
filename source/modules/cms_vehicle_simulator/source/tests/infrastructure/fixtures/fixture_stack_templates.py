# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# Standard Library
import tempfile
from unittest.mock import MagicMock

# Third Party Libraries
import pytest
from syrupy.extensions.json import JSONSnapshotExtension
from syrupy.matchers import path_value
from syrupy.types import SerializableData

# AWS Libraries
from aws_cdk import App, aws_lambda, aws_s3_deployment

# CMS Common Library
from cms_common.config.stack_inputs import S3AssetConfigInputs, SolutionConfigInputs

# Connected Mobility Solution on AWS
from ....infrastructure.cms_vehicle_simulator_stack import CmsVehicleSimulatorStack


@pytest.fixture(name="snapshot_json_with_matcher")
def fixture_snapshot_json_with_matcher(snapshot: SerializableData) -> SerializableData:
    matcher = path_value(
        mapping={
            ".*": r"(\/?([0-9a-fA-F]+)\.zip|[a-zA-Z0-9:/-]+(\d{12})[a-zA-Z0-9:/-]+)",
        },
        regex=True,
        types=(object,),
        replacer=lambda data, match: data.replace(match[1], "test") if match else data,
    )
    return snapshot.use_extension(JSONSnapshotExtension)(matcher=matcher)


@pytest.fixture(name="cms_vehicle_simulator_stack", scope="session")
def fixture_cms_vehicle_simulator_stack() -> CmsVehicleSimulatorStack:
    solution_config_inputs = SolutionConfigInputs(
        solution_id="test-solution-id",
        solution_name="test-solution-name",
        solution_version="test-solution-version",
        application_type="test-application-type",
        module_name="test-module-name",
        module_short_name="test-module-short-name",
        capability_id="test-capability-id",
    )
    s3_asset_config_inputs = S3AssetConfigInputs(
        bucket_base_name="test-bucket-base-name",
        object_key_prefix="test-object-key-prefix",
    )
    with (tempfile.TemporaryDirectory() as tmpdirname,):

        aws_lambda.Code.from_asset = MagicMock(  # type: ignore[method-assign]
            return_value=aws_lambda.AssetCode(path=tmpdirname)
        )

        aws_s3_deployment.Source.asset = MagicMock(  # type: ignore[method-assign]
            return_value=aws_s3_deployment.Source.data("test-source", "test-data")
        )

        app = App()
        stack = CmsVehicleSimulatorStack(
            app,
            "cms-vehicle-simulator-stack",
            solution_config_inputs=solution_config_inputs,
            s3_asset_config_inputs=s3_asset_config_inputs,
        )
        return stack
