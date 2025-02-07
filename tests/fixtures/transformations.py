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

"""Transformation test cases."""

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel
from schemapack import load_datapack, load_schemapack
from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.add_content_properties import (
    ADD_CONTENT_PROPERTIES_TRANSFORMATION,
)
from metldata.builtin_transformations.copy_content.main import (
    COPY_CONTENT_TRANSFORMATION,
)
from metldata.builtin_transformations.count_content_values.main import (
    COUNT_CONTENT_VALUES_TRANSFORMATION,
)
from metldata.builtin_transformations.count_references import (
    COUNT_REFERENCES_TRANSFORMATION,
)
from metldata.builtin_transformations.delete_content_subschema import (
    DELETE_CONTENT_SUBSCHEMA_TRANSFORMATION,
)
from metldata.builtin_transformations.delete_relations import (
    DELETE_RELATIONS_TRANSFORMATION,
)
from metldata.builtin_transformations.infer_relations import (
    RELATION_INFERENCE_TRANSFORMATION,
)
from metldata.builtin_transformations.sum_operation import (
    SUM_OPERATION_TRANSFORMATION,
)
from metldata.transform.base import TransformationDefinition
from tests.fixtures.data import ADVANCED_DATA
from tests.fixtures.models import ADVANCED_MODEL
from tests.fixtures.utils import BASE_DIR, read_yaml

HAPPY_TRANSFORMATION_DIR = BASE_DIR / "happy_transformations"
UNHAPPY_TRANSFORMATION_DIR = BASE_DIR / "unhappy_transformations"

TRANSFORMATIONS_BY_NAME: dict[str, TransformationDefinition] = {
    "infer_relations": RELATION_INFERENCE_TRANSFORMATION,
    "delete_content_subschema": DELETE_CONTENT_SUBSCHEMA_TRANSFORMATION,
    "add_content_properties": ADD_CONTENT_PROPERTIES_TRANSFORMATION,
    "count_references": COUNT_REFERENCES_TRANSFORMATION,
    "count_content_values": COUNT_CONTENT_VALUES_TRANSFORMATION,
    "sum_operation": SUM_OPERATION_TRANSFORMATION,
    "copy_content": COPY_CONTENT_TRANSFORMATION,
    "delete_relations": DELETE_RELATIONS_TRANSFORMATION,
}


@dataclass(frozen=True)
class TransformationTestCase:
    """A test case for a transformation."""

    transformation_name: str
    case_name: str
    transformation_definition: TransformationDefinition
    config: BaseModel
    input_model: SchemaPack
    input_data: DataPack
    transformed_model: SchemaPack
    transformed_data: DataPack

    def __str__(self) -> str:  # noqa: D105
        return f"{self.transformation_name}-{self.case_name}"


def _read_test_case(
    *, transformation_name: str, case_name: str, base_dir: Path
) -> TransformationTestCase:
    """Read a test case for a transformation."""
    transformation_definition = TRANSFORMATIONS_BY_NAME[transformation_name]
    case_dir = base_dir / transformation_name / case_name
    config_path = case_dir / "config.yaml"
    input_model_path = case_dir / "input.schemapack.yaml"
    input_data_path = case_dir / "input.datapack.yaml"
    transformed_model_path = case_dir / "transformed.schemapack.yaml"
    transformed_data_path = case_dir / "transformed.datapack.yaml"

    input_model = (
        load_schemapack(input_model_path)
        if input_model_path.exists()
        else ADVANCED_MODEL
    )
    input_data = (
        load_datapack(input_data_path) if input_data_path.exists() else ADVANCED_DATA
    )
    transformed_model = load_schemapack(transformed_model_path)
    transformed_data = load_datapack(transformed_data_path)
    config = transformation_definition.config_cls(**read_yaml(config_path))

    return TransformationTestCase(
        transformation_name=transformation_name,
        case_name=case_name,
        transformation_definition=transformation_definition,
        config=config,
        input_model=input_model,
        input_data=input_data,
        transformed_model=transformed_model,
        transformed_data=transformed_data,
    )


def _read_test_case_variant(transformation_base_dir: Path, transformation_name: str):
    """Read from specific base dir to distinguish between happy/unhappy test cases."""
    transformation_dir = transformation_base_dir / transformation_name
    test_cases = []

    if transformation_dir.exists():
        for path in transformation_dir.iterdir():
            if path.is_dir():
                test_cases.append(
                    _read_test_case(
                        transformation_name=transformation_name,
                        case_name=path.name,
                        base_dir=transformation_base_dir,
                    )
                )
    return test_cases


def _read_all_test_cases() -> (
    tuple[list[TransformationTestCase], list[TransformationTestCase]]
):
    """Read all test cases for a transformation."""
    happy_test_cases = []
    unhappy_test_cases = []

    for transformation_name in TRANSFORMATIONS_BY_NAME:
        happy_test_cases.extend(
            _read_test_case_variant(
                transformation_base_dir=HAPPY_TRANSFORMATION_DIR,
                transformation_name=transformation_name,
            )
        )
        unhappy_test_cases.extend(
            _read_test_case_variant(
                transformation_base_dir=UNHAPPY_TRANSFORMATION_DIR,
                transformation_name=transformation_name,
            )
        )

    return happy_test_cases, unhappy_test_cases


HAPPY_TEST_CASES, UNHAPPY_TEST_CASES = _read_all_test_cases()
