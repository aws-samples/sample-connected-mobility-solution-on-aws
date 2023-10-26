# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# Standard Library
from enum import Enum


class CustomResourceType:
    class RequestType(Enum):
        CREATE = "Create"
        UPDATE = "Update"
        DELETE = "Delete"

    class ResourceType(Enum):
        MANAGE_USER_POOL_DOMAIN = "ManageUserPoolDomain"

    class StatusType(Enum):
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"
