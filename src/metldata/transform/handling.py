# Copyright 2021 - 2025 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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
#

"""Logic for handling Transformation."""

from typing import override

import schemapack.exceptions
from schemapack import SchemaPackValidator
from schemapack._internals.validation.base import (
    ClassValidationPlugin,
    GlobalValidationPlugin,
    ResourceValidationPlugin,
)
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.transform.base import (
    Config,
    TransformationDefinition,
)
from metldata.transform.exceptions import (
    PostTransformValidationError,
    PreTransformValidationError,
)


class NoOpValidator(SchemaPackValidator):
    """Custom no-op variant of the SchemaPackValidator used for skipping validation."""

    @override
    def __init__(
        self,
        *,
        schemapack: SchemaPack,
        add_global_plugins: list[type[GlobalValidationPlugin]] | None = None,
        add_class_plugins: list[type[ClassValidationPlugin]] | None = None,
        add_resource_plugins: list[type[ResourceValidationPlugin]] | None = None,
    ):
        """Do nothing with the input, just skip plugin creation."""

    @override
    def validate(self, *, datapack: DataPack):
        """Do nothing and return."""
        return


class TransformationHandler[SubmissionAnnotation]:
    """Used for executing transformations described in a TransformationDefinition."""

    def __init__(
        self,
        transformation_definition: TransformationDefinition[Config],
        transformation_config: Config,
        input_model: SchemaPack,
        validate_input: bool = False,
        validate_output: bool = False,
    ):
        """Initialize the TransformationHandler by checking the assumptions made on the
        input model and transforming the model as described in the transformation
        definition. The transformed model is available at the `transformed_model`
        attribute.

        Raises:
            ModelAssumptionError:
                if the assumptions made on the input model are not met.
        """
        self._definition = transformation_definition
        self._config = transformation_config
        self._input_model = input_model

        self._definition.check_model_assumptions(self._input_model, self._config)
        self.transformed_model = self._definition.transform_model(
            self._input_model, self._config
        )
        self._data_transformer = self._definition.data_transformer_factory(
            config=self._config,
            input_model=self._input_model,
            transformed_model=self.transformed_model,
        )
        self._input_data_validator = (
            SchemaPackValidator(schemapack=self._input_model)
            if validate_input
            else NoOpValidator(schemapack=self._input_model)
        )
        self._transformed_data_validator = (
            SchemaPackValidator(schemapack=self.transformed_model)
            if validate_output
            else NoOpValidator(schemapack=self.transformed_model)
        )

    def transform_data(
        self, data: DataPack, annotation: SubmissionAnnotation
    ) -> DataPack:
        """Transforms data using the transformation definition. Validates the
        input data against the input model and the transformed data
        against the transformed model.

        Args:
            data: The data to be transformed.

        Raises:
            PreTransformValidation:
                If validation of input data fails against the input model.
            PostTransformValidation:
                If validation of transformed data fails against the transformed model.
            DataTransformationError:
                if the transformation fails.
        """
        try:
            self._input_data_validator.validate(datapack=data)
        except schemapack.exceptions.ValidationError as error:
            raise PreTransformValidationError(validation_error=error) from error

        transformed_data = self._data_transformer.transform(
            data=data, annotation=annotation
        )

        try:
            self._transformed_data_validator.validate(datapack=transformed_data)
        except schemapack.exceptions.ValidationError as error:
            raise PostTransformValidationError(validation_error=error) from error

        return transformed_data
