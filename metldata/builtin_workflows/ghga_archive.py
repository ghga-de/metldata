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

"""A GHGA Archive-specific workflow."""

from metldata.builtin_transformations.add_accessions import (
    ACCESSION_ADDITION_TRANSFORMATION,
)
from metldata.builtin_transformations.custom_embeddings import (
    CUSTOM_EMBEDDING_TRANSFORMATION,
)
from metldata.builtin_transformations.delete_slots import SLOT_DELETION_TRANSFORMATION
from metldata.builtin_transformations.infer_references import (
    REFERENCE_INFERENCE_TRANSFORMATION,
)
from metldata.builtin_transformations.merge_slots import SLOT_MERGING_TRANSFORMATION
from metldata.transform.base import WorkflowDefinition, WorkflowStep

GHGA_ARCHIVE_WORKFLOW = WorkflowDefinition(
    description=(
        "A GHGA Archive-specific workflow implementing the steps as defined here:"
        + " https://docs.ghga-dev.de/main/architecture_concepts/ac002_metadata_lifecycl"
        + "e.html"
    ),
    steps={
        "add_accessions": WorkflowStep(
            description="Add accessions that replace aliases as identifiers.",
            transformation_definition=ACCESSION_ADDITION_TRANSFORMATION,
            input=None,
        ),
        "infer_multiway_references": WorkflowStep(
            description=(
                "Infer multi-way references. During submission, references between"
                + " two classes are only establish in a uni-lateral way from one of the"
                + " interlinked classes. Here references from both sides are"
                + " established. Moreover, shortcuts between entities that are"
                + " connected via a common reference are established."
            ),
            transformation_definition=REFERENCE_INFERENCE_TRANSFORMATION,
            input="add_accessions",
        ),
        "get_dataset_file_summary": WorkflowStep(
            description=(
                "Generate a slot in that dataset that combines all files of different"
                + " type into a single list."
            ),
            transformation_definition=SLOT_MERGING_TRANSFORMATION,
            input="infer_multiway_references",
        ),
        "embed_restricted_dataset": WorkflowStep(
            description=(
                "A step to generate a fully embedded dataset for data recepients that"
                + " have been granted controlled access to that dataset."
            ),
            transformation_definition=CUSTOM_EMBEDDING_TRANSFORMATION,
            input="infer_multiway_references",
        ),
        "remove_restricted_metadata": WorkflowStep(
            description=(
                "Restricted metadata that shall not be publicly accessible is removed."
            ),
            transformation_definition=SLOT_DELETION_TRANSFORMATION,
            input="infer_multiway_references",
        ),
        "embed_public_dataset": WorkflowStep(
            description=(
                "A step to generate a fully embedded dataset for use in the metadata"
                + " catalog as the single dataset view."
            ),
            transformation_definition=SLOT_DELETION_TRANSFORMATION,
            input="remove_restricted_metadata",
        ),
    },
    artifacts={
        "resolved_restricted": "get_dataset_file_summary",
        "embedded_restricted_dataset": "embed_restricted_dataset",
        "resolved_public": "remove_restricted_metadata",
        "embedded_public_dataset": "embed_public_dataset",
    },
)
