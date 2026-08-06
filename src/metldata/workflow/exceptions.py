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

import pydantic


class UnknownTransformationError(Exception):
    """Raised when a transformation name is not found in the transformation registry."""


class DataPackModelValidationError(Exception):
    """Raised when the final datapack of a workflow fails DataPack model validation.

    The builtin transformations build datapacks via structural sharing (``model_copy``),
    which bypasses DataPack model validation. The workflow re-validates the final
    datapack through the DataPack model to enforce the spec-level constraints that
    ``SchemaPackValidator`` does not cover: field types, ``ResourceId`` constraints, and
    referential integrity.
    """

    def __init__(self, *, validation_error: pydantic.ValidationError):
        super().__init__(
            "The final datapack of the workflow failed DataPack model validation:"
            + f"\n{validation_error}"
        )
        self.error = validation_error


class ModelNotFoundError(FileNotFoundError):
    """Raised when a model file is not found in the model registry."""


class WorkflowValidationError(Exception):
    """Raised when a workflow contains operations that reference unknown or unregistered transformations."""


class WorkflowExecutionError(Exception):
    """Raised when a workflow execution fails during model or data transformation."""

    def __init__(self, *, step_index: int, step_name: str, error: Exception):
        super().__init__(
            f"Error occurred while executing workflow step {step_index} ('{step_name}'): {error}"
        )
        self.error = error
        self._step_index = step_index
        self._step_name = step_name
