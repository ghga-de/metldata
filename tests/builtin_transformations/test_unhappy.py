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

"""Test the unhappy paths of the builtin transformations"""

import pytest
from schemapack.spec.datapack import DataPack

from metldata.builtin_transformations.add_class.data_transform import add_data_class
from metldata.builtin_transformations.replace_resource_ids.data_transform import (
    replace_data_resource_ids,
)
from metldata.transform.exceptions import InvalidAnnotationError
from tests.fixtures.annotation import Annotation

_DATA = DataPack.model_validate(
    {
        "datapack": "4.2.0",
        "resources": {
            "Sample": {"sample_x": {"content": {}}},
        },
    }
)


@pytest.mark.parametrize(
    "accession_map",
    [
        {"sample_x": ""},
        {"": "SAMPLE_NEW_0001"},
    ],
    ids=["empty_new_id", "empty_old_id"],
)
def test_replace_data_resource_ids_rejects_empty_accession_ids(
    accession_map: dict[str, str],
):
    """An empty old or new id in the accession map is rejected at the boundary."""
    annotation = Annotation(accession_map={"Sample": accession_map})

    with pytest.raises(InvalidAnnotationError):
        replace_data_resource_ids(
            data=_DATA, class_name="Sample", annotation=annotation
        )


def test_add_data_class_rejects_empty_resource_id():
    """An empty resource id in the annotation's resources is rejected at the
    boundary.
    """
    annotation = Annotation(added_class_resources={"Dataset": {"": {}}})

    with pytest.raises(InvalidAnnotationError):
        add_data_class(
            data=_DATA,
            annotation=annotation,
            class_name="Dataset",
            content_schema={"type": "object", "properties": {}},
            relations=[],
        )
