"""Handlers for CRUD of a CloudFormation Resource
that will set the StepConcurrencyLevel attribute
of an EMR cluster.
"""
import logging
from typing import Any, MutableMapping, Optional

from cloudformation_cli_python_lib import (
    Action,
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
    exceptions,
)

from .models import ResourceHandlerRequest, ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel("INFO")
TYPE_NAME = "JB::EMR::StepConcurrencyLevel"

resource = Resource(TYPE_NAME, ResourceModel)  # pylint: disable=invalid-name
test_entrypoint = resource.test_entrypoint  # pylint: disable=invalid-name


def get_cluster_info(session: Optional[SessionProxy], cluster_id: str) -> dict:
    """This function will gather all information from a describe cluster
    call to the given cluster ID

    Attributes:
        session (Optional[SessionProxy]): The session proxy for connecting
            to the needed AWS API client
        cluster_id (str): The unique ID of the cluster to get details from

    Returns:
        dict: A dictionary of the cluster attributes
    """
    client = session.client('emr')
    LOG.info("Getting all info for cluster %s", cluster_id)
    response = client.describe_cluster(
        ClusterId=cluster_id
    )
    LOG.info("RESPONSE: %s", response)
    return response


def get_uid(session: Optional[SessionProxy], cluster_id: str) -> str:
    """This function will retreive the value of the tag "StepConcurrencyUID"
    from the given cluster ID

    Attributes:
        session (Optional[SessionProxy]): The session proxy for connecting
            to the needed AWS API client
        cluster_id (str): The unique ID of the cluster to get details from

    Returns:
        str: The value of the StepConcurrencyUID tag in the cluster
    """
    response = get_cluster_info(session, cluster_id)
    LOG.info("Gathering tags for cluster %s", cluster_id)
    tags = response["Cluster"]["Tags"]
    LOG.info(tags)
    for tag in tags:
        if tag['Key'] == "StepConcurrencyUID":
            LOG.info("Found concurrency tag")
            LOG.info(tag["Value"])
            return tag["Value"]
    LOG.info("Didn't find concurrency tag")
    return None


def get_concurrency_level(session: Optional[SessionProxy], cluster_id: str) -> str:
    """This function will retreive the current value of StepConcurrencyLevel
    from the given cluster

    Attributes:
        session (Optional[SessionProxy]): The session proxy for connecting
            to the needed AWS API client
        cluster_id (str): The unique ID of the cluster to get details from

    Returns:
        str: The value of the StepConcurrencyLevel attribute in the cluster
    """
    response = get_cluster_info(session, cluster_id)
    LOG.info("Gathering concurrency for cluster %s", cluster_id)
    return response["Cluster"]["StepConcurrencyLevel"]


@resource.handler(Action.CREATE)
def create_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],  # pylint: disable=unused-argument
) -> ProgressEvent:
    """This function is triggered by the CloudFormation CREATE event
    and will set the StepConcurrency level from the default of 1
    to the new provided value within the up to the max of 256. It
    will also add a tag to the cluster in order to keep track of
    the resource.

    Attributes:
        session (Optional[SessionProxy]): The session proxy for connecting
            to the needed AWS API client
        cluster_id (str): The unique ID of the cluster to get details from
        callback_context (MutableMapping[str, Any]): Use to store any state
            between re-invocation via IN_PROGRESS

    Returns:
        ProgressEvent: An event with the status of the action
    """
    LOG.info("Create Handler")
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    model.UID = "cluster:" + model.ClusterId
    model.StepConcurrencyLevel = int(model.StepConcurrencyLevel)
    uid = get_uid(session, model.ClusterId)
    LOG.info("UID: %s", uid)
    if uid == model.UID:
        raise exceptions.AlreadyExists(TYPE_NAME, model.ClusterId)
    if model.StepConcurrencyLevel < 1 or model.StepConcurrencyLevel > 256:
        raise exceptions.InvalidRequest(
            f"Step Concurency Level must be between 1 and 256, \
                {model.StepConcurrencyLevel} was given.")
    try:
        client = session.client('emr')
        LOG.info("Setting concurrency to %s for cluster %s",
                 model.StepConcurrencyLevel, model.ClusterId)
        response = client.modify_cluster(
            ClusterId=model.ClusterId,
            StepConcurrencyLevel=int(model.StepConcurrencyLevel)
        )
        LOG.info("RESPONSE TO SET CONCURRENCY:")
        LOG.info(response)
        LOG.info("Setting UID tag to %s", model.ClusterId)
        tag_response = client.add_tags(
            ResourceId=model.ClusterId,
            Tags=[
                {
                    "Key": "StepConcurrencyUID",
                    "Value": model.UID
                }
            ]
        )
        LOG.info("RESPONSE TO ADD TAGS:")
        LOG.info(tag_response)
        progress.status = OperationStatus.SUCCESS
    except Exception as unexpected_exception:
        LOG.error(str(unexpected_exception))
        raise exceptions.InternalFailure(
            f"Failed Create: {str(unexpected_exception)}")
    return progress


@resource.handler(Action.UPDATE)
def update_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],  # pylint: disable=unused-argument
) -> ProgressEvent:
    """This function is triggered by the CloudFormation UPDATE event
    and will update the StepConcurrency level to the new provided
    value within the up to the max of 256. It will also add a tag to
    the cluster in order to keep track of the resource.

    Attributes:
        session (Optional[SessionProxy]): The session proxy for connecting
            to the needed AWS API client
        cluster_id (str): The unique ID of the cluster to get details from
        callback_context (MutableMapping[str, Any]): Use to store any state
            between re-invocation via IN_PROGRESS

    Returns:
        ProgressEvent: An event with the status of the action
    """
    model = request.desiredResourceState
    previous_model = request.previousResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    LOG.info("UPDATE HANDLER")
    LOG.info("MODEL")
    LOG.info(model)
    LOG.info("PREVIOUS")
    LOG.info(previous_model)
    model.StepConcurrencyLevel = int(model.StepConcurrencyLevel)
    if model.UID != previous_model.UID:
        raise exceptions.InvalidRequest("Cannot update the UID")
    if model.StepConcurrencyLevel < 1 or model.StepConcurrencyLevel > 256:
        raise exceptions.InvalidRequest(
            f"Step Concurency Level must be between 1 and 256, \
                {model.StepConcurrencyLevel} was given.")
    if model.UID != get_uid(session, model.ClusterId):
        raise exceptions.NotFound(TYPE_NAME, model.ClusterId)
    try:
        client = session.client('emr')
        LOG.info("Updating concurrency to %s for cluster %s",
                 model.StepConcurrencyLevel, model.ClusterId)
        response = client.modify_cluster(
            ClusterId=model.ClusterId,
            StepConcurrencyLevel=model.StepConcurrencyLevel
        )
        LOG.info("RESPONSE: %s", response)
        progress.status = OperationStatus.SUCCESS
    except Exception as unexpected_exception:
        LOG.error(str(unexpected_exception))
        raise exceptions.InternalFailure(
            f"Failed Update: {str(unexpected_exception)}")
    return progress


@resource.handler(Action.DELETE)
def delete_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],  # pylint: disable=unused-argument
) -> ProgressEvent:
    """This function is triggered by the CloudFormation DELETE event
    and will set the StepConcurrency level to the default of 1.
    It will also remove a tag on the cluster in order to keep track of
    the resource.

    Attributes:
        session (Optional[SessionProxy]): The session proxy for connecting
            to the needed AWS API client
        cluster_id (str): The unique ID of the cluster to get details from
        callback_context (MutableMapping[str, Any]): Use to store any state
            between re-invocation via IN_PROGRESS

    Returns:
        ProgressEvent: An event with the status of the action
    """
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    LOG.info("DELETE HANDLER")
    if get_uid(session, model.ClusterId) != model.UID:
        raise exceptions.NotFound(TYPE_NAME, model.ClusterId)
    try:
        client = session.client('emr')
        LOG.info("Setting concurrency to default for cluster %s",
                 model.ClusterId)
        response = client.modify_cluster(
            ClusterId=model.ClusterId,
            StepConcurrencyLevel=1
        )
        LOG.info("RESPONSE:")
        LOG.info("RESPONSE:")
        LOG.info(response)
        progress.resourceModel = None
        LOG.info("Removing Tags")
        tags_response = client.remove_tags(
            ResourceId=model.ClusterId,
            TagKeys=["StepConcurrencyUID"]
        )
        LOG.info("TAG REMOVAL RESPONSE")
        LOG.info(tags_response)
        LOG.info("TAG REMOVAL RESPONSE: %s", tags_response)
        progress.status = OperationStatus.SUCCESS
    except Exception as unexpected_exception:
        LOG.error(str(unexpected_exception))
        raise exceptions.InternalFailure(
            f"Failed Delete: {str(unexpected_exception)}")
    return progress


@resource.handler(Action.READ)
def read_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],  # pylint: disable=unused-argument
) -> ProgressEvent:
    """This function is triggered by the CloudFormation READ event
    and will retrieve the StepConcurrency level of the cluster.

    Attributes:
        session (Optional[SessionProxy]): The session proxy for connecting
            to the needed AWS API client
        cluster_id (str): The unique ID of the cluster to get details from
        callback_context (MutableMapping[str, Any]): Use to store any state
            between re-invocation via IN_PROGRESS

    Returns:
        ProgressEvent: An event with the status of the action
    """
    model = request.desiredResourceState
    if model.UID != get_uid(session, model.ClusterId):
        raise exceptions.NotFound(TYPE_NAME, model.ClusterId)
    try:
        model.StepConcurrencyLevel = get_concurrency_level(
            session, model.ClusterId)
    except Exception as unexpected_exception:
        LOG.error(str(unexpected_exception))
        raise exceptions.InternalFailure(
            f"Failed Read: {str(unexpected_exception)}")
    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModel=model,
    )
