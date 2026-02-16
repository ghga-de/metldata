# Copyright 2021 - 2026 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
# for the German Human Genome-Phenome Archive (GHGA)
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

"""Workflow validation logic."""

from metldata.transform.base import TransformationDefinition
from metldata.workflow.base import Workflow
from metldata.workflow.exceptions import WorkflowValidationError


def validate_workflow_against_registry(
    workflow: Workflow, transformation_registry: dict[str, TransformationDefinition]
) -> None:
    """Validate a workflow against a transformation registry.

    At this stage, the workflow has already been parsed into a ``Workflow``
    instance and is assumed to be structurally valid. This function performs
    semantic validation by ensuring that:

    1. Each referenced transformation exists in the registry.
    2. The provided operation arguments are compatible with the
    transformation's expected configuration class.

    Args:
        workflow: The workflow instance to validate.
        transformation_registry: Mapping of transformation names to their
            corresponding definitions.

    Raises:
        WorkflowValidationError: If a referenced transformation does not exist
            or if the provided configuration is incompatible with the
            transformation definition.
    """
    if not transformation_registry:
        raise WorkflowValidationError("Transformation registry cannot be empty.")

    for operation in workflow.operations:
        if operation.name not in transformation_registry:
            raise WorkflowValidationError(
                f"Unknown transformation '{operation.name}' referenced in workflow."
            )

        transformation_definition = transformation_registry[operation.name]
        provided_operation_config = operation.args
        expected_config_class = transformation_definition.config_cls

        # Validate by trying to create a valid config instance
        if not isinstance(provided_operation_config, expected_config_class):
            try:
                expected_config_class(**provided_operation_config)
            except Exception as error:
                raise WorkflowValidationError(
                    f"Invalid configuration for transformation '{operation.name}'. "
                    f"Provided arguments {provided_operation_config} are not "
                    f"compatible with expected config type "
                    f"{expected_config_class.__name__}."
                ) from error
