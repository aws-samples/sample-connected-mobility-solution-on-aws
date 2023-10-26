# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# Standard Library
import os
import time
from typing import Any, Dict, Generator, List, Optional

# Third Party Libraries
import boto3
from aws_lambda_powertools import Logger, Tracer
from botocore.config import Config
from botocore.exceptions import ClientError

tracer = Tracer()
logger = Logger()


class DynHelpers:
    dynamo_object = None

    @staticmethod
    def dyn_resource() -> Any:
        if getattr(DynHelpers, "dynamo_object"):
            return DynHelpers.dynamo_object

        DynHelpers.dynamo_object = boto3.resource(
            "dynamodb",
            region_name=os.environ.get("REGION_NAME"),
            config=Config(user_agent_extra=os.environ["USER_AGENT_STRING"]),
        )
        return DynHelpers.dynamo_object

    @staticmethod
    def get_all(*args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return [
            item for result in DynHelpers.dyn_scan(*args, **kwargs) for item in result
        ]

    @staticmethod
    def put_item(table_name: str, item: Dict[str, Any]) -> None:
        utcnow = str(time.time())
        if not item.get("created_datetime"):
            item["created_datetime"] = utcnow
        item["updated_datetime"] = utcnow

        try:
            DynHelpers.dyn_resource().Table(table_name).put_item(Item=item)
        except ClientError as err:
            logger.error(
                "Couldn't update item %s to table %s. Here's why: %s: %s",
                item,
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    @staticmethod
    def get_item(table_name: str, get_criteria: Dict[str, Any]) -> Any:
        try:
            response = (
                DynHelpers.dyn_resource().Table(table_name).get_item(Key=get_criteria)
            )
            return response["Item"]
        except ClientError as err:
            logger.error(
                "Couldn't get item %s from table %s. Here's why: %s: %s",
                get_criteria,
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        except KeyError:
            logger.error(
                "Item %s not found in table %s.",
                get_criteria,
                table_name,
                exc_info=True,
            )
            raise

    @staticmethod
    def update_item(
        table_name: str,
        item: Dict[str, Any],
        update_expression: Optional[str] = None,
        expression_attr: Optional[Dict[str, Any]] = None,
        return_values: str = "UPDATED_NEW",
    ) -> Any:
        try:
            response = (
                DynHelpers.dyn_resource()
                .Table(table_name)
                .update_item(
                    Key=item,
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_attr,
                    ReturnValues=return_values,
                )
            )
        except ClientError as err:
            logger.error(
                "Couldn't update item %s to table %s. Here's why: %s: %s",
                item,
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

        return response["Attributes"]

    @staticmethod
    def delete_item(table_name: str, delete_keys: dict[str, Any]) -> None:
        try:
            DynHelpers.dyn_resource().Table(table_name).delete_item(Key=delete_keys)

        except ClientError as err:
            logger.error(
                "Couldn't delete item %s from table %s. Here's why: %s: %s",
                id,
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    @staticmethod
    def dyn_batch_get(batch_keys: Dict[str, Any]) -> Dict[str, List[Any]]:
        remaining_tries = 5
        sleepy_time = 1  # Start with 1 second of sleep, then exponentially increase.
        retrieved: Dict[str, List[Any]] = {key: [] for key in batch_keys}
        while batch_keys and remaining_tries:
            response = DynHelpers.dyn_resource().batch_get_item(RequestItems=batch_keys)
            # Collect any retrieved items and retry unprocessed keys.
            for key in response.get("Responses", []):
                retrieved[key] += response["Responses"][key]

            batch_keys = response["UnprocessedKeys"]

            logger.info(
                "%s unprocessed keys returned. Sleep, then retry.",
                len(batch_keys),
            )
            remaining_tries -= 1
            if batch_keys and remaining_tries:
                logger.info("Sleeping for %s seconds.", sleepy_time)
                time.sleep(sleepy_time)
                sleepy_time = min(sleepy_time * 2, 32)

        return retrieved

    @staticmethod
    def dyn_scan(
        *args: Any, table: Optional[str] = None, **kwargs: Any
    ) -> Generator[List[Dict[str, Any]], None, None]:
        scan_kwargs = {k: v for k, v in kwargs.items() if v}

        logger.info("Running dynamo scan on %s", table, extra={"kwargs": scan_kwargs})

        while scan_kwargs.get("LastEvaluatedKey", "start"):
            if scan_kwargs.get("LastEvaluatedKey", None):
                scan_kwargs["ExclusiveStartKey"] = scan_kwargs.pop("LastEvaluatedKey")

            try:
                response = DynHelpers.dyn_resource().Table(table).scan(**scan_kwargs)
                logger.info("Scan response %s", table, extra={"response": response})
                scan_kwargs["LastEvaluatedKey"] = response.get("LastEvaluatedKey")

                yield response.get("Items")
            except ClientError as err:
                logger.error(
                    "Couldn't scan %s. Here's why: %s: %s",
                    table,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
