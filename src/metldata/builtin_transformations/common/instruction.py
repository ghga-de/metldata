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

"Generic instruction type protocols."

from typing import Protocol, TypeVar

from metldata.builtin_transformations.common import NewContentSchemaPath, SourcePath


class InstructionProtocol(Protocol):
    """Instruction definition."""

    class_name: str


class TargetInstructionProtocol(Protocol):
    """Instruction definition for target instruction."""

    class_name: str
    target_content: NewContentSchemaPath


class SourceInstructionProtocol(Protocol):
    """Instruction definition for source instruction"""

    class_name: str
    source: SourcePath


class TargetSourceInstructionProtocol(Protocol):
    """Instruction definition for both target and source dependent instructions."""

    class_name: str
    target_content: NewContentSchemaPath
    source: SourcePath


TargetInstruction = TypeVar("TargetInstruction", bound=TargetInstructionProtocol)
SourceInstruction = TypeVar("SourceInstruction", bound=SourceInstructionProtocol)
TargetSourceInstruction = TypeVar(
    "TargetSourceInstruction", bound=TargetSourceInstructionProtocol
)
Instruction = TypeVar(
    "Instruction", bound=TargetInstructionProtocol | SourceInstructionProtocol
)
