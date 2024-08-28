# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=unused-import

# Connected Mobility Solution on AWS
from .fixtures.fixture_shared import (
    fixture_aws_credentials_env_vars,
    fixture_mock_env_vars,
    fixture_mock_module_env_vars,
)
from .handlers.fixtures.fixture_api import (
    fixture_create_device_type_event,
    fixture_create_event,
    fixture_create_simulation_event,
    fixture_create_template_event,
    fixture_env_vars,
    fixture_update_device_type_event,
    fixture_update_simulation_by_id_event,
    fixture_update_simulations_event,
)
from .handlers.fixtures.fixture_api_data import (
    fixture_dynamodb_table,
    fixture_step_function,
)
from .handlers.fixtures.fixture_custom_resource import (
    fixture_context,
    fixture_custom_resource_create_event,
    fixture_custom_resource_delete_event,
    fixture_custom_resource_event,
    fixture_custom_resource_update_event,
)
from .handlers.fixtures.fixture_provision import (
    fixture_cleanup_event,
    fixture_device_provisioner,
    fixture_provision_event,
    fixture_provisioned_policy,
    fixture_provisioned_secrets,
    fixture_provisioned_thing,
)
from .handlers.fixtures.fixture_simulate import (
    fixture_limits,
    fixture_simulate_data_event,
)
from .infrastructure.fixtures.fixture_stack_templates import (
    fixture_cms_vehicle_simulator_stack,
    fixture_snapshot_json_with_matcher,
)
