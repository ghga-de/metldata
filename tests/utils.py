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

"""Utility functions for testing."""

import json
from difflib import unified_diff

from schemapack.spec.datapack import DataPack
from schemapack.spec.schemapack import SchemaPack

from metldata.builtin_transformations.common.utils import data_to_dict, model_to_dict


def compare_model(transformed_model: SchemaPack, test_case_model: SchemaPack):
    """If models don't match, compare the serialized versions.

    This produces a line by line diff which is more informative for debugging
    """
    if transformed_model != test_case_model:
        model_diff = unified_diff(
            json.dumps(
                model_to_dict(transformed_model), indent=2, sort_keys=True
            ).splitlines(),
            json.dumps(
                model_to_dict(test_case_model), indent=2, sort_keys=True
            ).splitlines(),
            fromfile="transformed_model",
            tofile="test_case_model",
            n=5,
        )
        output = f"\n{'\n'.join(model_diff)}"
        raise AssertionError(output)


def compare_data(transformed_data: DataPack, test_case_data: DataPack):
    """If data packs don't match, compare the serialized versions.

    This produces a line by line diff which is more informative for debugging
    """
    if transformed_data != test_case_data:
        data_diff = unified_diff(
            json.dumps(
                data_to_dict(transformed_data), indent=2, sort_keys=True
            ).splitlines(),
            json.dumps(
                data_to_dict(test_case_data), indent=2, sort_keys=True
            ).splitlines(),
            fromfile="transformed_data",
            tofile="test_case_data",
            n=5,
        )
        output = f"\n{'\n'.join(data_diff)}"
        raise AssertionError(output)
