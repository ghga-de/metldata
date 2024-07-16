# Copyright 2021 - 2024 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Test relations utils."""

from metldata.builtin_transformations.common.path.path import (
    RelationPath,
)
from metldata.builtin_transformations.infer_relations.config import (
    RelationInferenceConfig,
)
from metldata.builtin_transformations.infer_relations.relations import (
    InferenceInstruction,
)


def test_config():
    """Test the RelationInferenceConfig class."""
    inferred_relations = {
        "class_a": {
            "class_d": {
                "path": "class_a(class_b)>class_b(class_d)>class_d",
            },
            "class_c": {
                "path": "class_a(class_b)>class_b<(class_c)class_c",
            },
        },
        "class_b": {
            "class_c": {
                "path": "class_b<(class_c)class_c",
            }
        },
    }
    expected_refs = [
        InferenceInstruction(
            source="class_a",
            target="class_d",
            path=RelationPath(path_str="class_a(class_b)>class_b(class_d)>class_d"),
            new_property="class_d",
        ),
        InferenceInstruction(
            source="class_a",
            target="class_c",
            path=RelationPath(path_str="class_a(class_b)>class_b<(class_c)class_c"),
            new_property="class_c",
        ),
        InferenceInstruction(
            source="class_b",
            target="class_c",
            path=RelationPath(path_str="class_b<(class_c)class_c"),
            new_property="class_c",
        ),
    ]

    config = RelationInferenceConfig(inferred_relations=inferred_relations)  # type: ignore
    observed_refs = config.inference_instructions
    assert expected_refs == observed_refs
