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

"""Defining exceptions."""


class ModelAssumptionError(RuntimeError):
    """Raised when assumptions made by transformation step about a model are not met."""


class MultiplicityError(ModelAssumptionError):
    """Raised when a relation in the model does not conform to the required multiplicity
    constraints. It occurs when the actual cardinality of a relationship within a model
    fails to meet the expected multiplicity criteria of a transformation. E.g.,
    in 'count references' transformation, the target of a relation is required to
    contribute multiple instances(`target=True`) to the relation, and this error is raised
    if that condition is not satisfied.
    """


class NotDirectRelationError(ModelAssumptionError):
    """Raised when a relation_path describes an indirect relation between two classes.
    A direct relation is when a class directly refers to another class through
    its relations. That relation can be denoted both with active and passive relation
    types (e.g. 'A(relation_b)>B', 'B<(relation_b)A)'.
    """


class ModelTransformationError(RuntimeError):
    """Raised when a transformation failed when applied to the schemapack-based model.
    This exception should only be raised when the error could not have been caught
    earlier by model assumption checks (otherwise the AssumptionsInsufficiencyError
    should be raised instead).
    """


class DataTransformationError(RuntimeError):
    """Raised when a transformation failed when applied to data in datapack-format.
    This exception should only be raised when the error could not have been caught
    earlier by model assumption checks (otherwise the EvitableTransformationError
    should be raised instead).
    """


class EvitableTransformationError(RuntimeError):
    """Raised when an exception during the model or data transformation should have
    been caught earlier by model assumption or data validation checks.
    """

    def __init__(self):
        super().__init__(
            "This unexpected error appeared during transformation, however, it should"
            + " have been caught earlier during model assumption checks (and/or by data"
            + " validation against the assumption-checked model). Please make sure that"
            + " the model assumption checks guarantee the workability of the"
            + " corresponding transformation wrt the provided model (and/or data)."
        )
