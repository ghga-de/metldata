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


"""Defining workflow related exceptions."""

from metldata.transform.handling import TransformationHandler


class UnknownTransformationError(Exception):
    """Raised when a transformation name is not found in the transformation registry."""


class ModelNotFoundError(FileNotFoundError):
    """Raised when a model file is not found in the model registry."""


class WorkflowValidationError(Exception):
    """Raised when a workflow contains operations that reference unknown or unregistered transformations."""


class WorkflowExecutionError(Exception):
    """Raised when a workflow executes fails due to an error during the execution of a
    transformation.
    """

    def __init__(
        self, *, transformation_handler: TransformationHandler, error: Exception
    ):
        """Initialize the workflow execution error."""
        super().__init__(
            f"Error occurred while executing workflow: {transformation_handler}: {error}"
        )
