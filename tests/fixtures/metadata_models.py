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

"""Metadata models."""

from tests.fixtures.utils import BASE_DIR

MINIMAL_VALID_METADATA_MODEL = BASE_DIR / "minimal_model.yaml"
ADVANCED_VALID_METADATA_MODEL = BASE_DIR / "advanced_model.yaml"
VALID_METADATA_MODELS = [MINIMAL_VALID_METADATA_MODEL, ADVANCED_VALID_METADATA_MODEL]

ROOT_CLASS_INVALID_MODELS = [
    BASE_DIR / "minimal_model_root_class_invalid1.yaml",
    BASE_DIR / "minimal_model_root_class_invalid2.yaml",
]

ANCHORS_INVALID_MODELS = [
    BASE_DIR / "minimal_model_anchors_invalid1.yaml",
    BASE_DIR / "minimal_model_anchors_invalid2.yaml",
    BASE_DIR / "minimal_model_anchors_invalid3.yaml",
    BASE_DIR / "minimal_model_anchors_invalid4.yaml",
]

INVALID_METADATA_MODELS = ROOT_CLASS_INVALID_MODELS + ANCHORS_INVALID_MODELS
