# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

"""Logic to check basic assumption about the metadata model."""

from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView

ROOT_CLASS = "Submission"


class MetadataModelAssumptionError(RuntimeError):
    """Raised when the assumptions about the metadata model are not met"""


def check_metadata_model_assumption(*, model_path: Path) -> None:
    """Check that the basic assumptions that metldata makes about the metadata model
    are met. Raises a MetadataModelAssumptionError otherwise."""

    schema_view = SchemaView(schema=str(model_path))

    # has a tree root called ROOT_CLASS:
    submission_class = schema_view.get_class(class_name=ROOT_CLASS, imports=False)

    if submission_class is None:
        raise MetadataModelAssumptionError(
            "A submission class is required but does not exist."
        )

    if not submission_class.tree_root:
        raise MetadataModelAssumptionError(
            "The submission class must have the tree_root property set to true."
        )
