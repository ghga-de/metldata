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
#

"""Registry builder for built-in transformations."""

from collections.abc import Callable
from typing import Any, TypeVar

from metldata.transform.base import TransformationDefinition

T = TypeVar("T", bound=TransformationDefinition[Any])

_TRANSFORMATION_REGISTRY: dict[str, TransformationDefinition[Any]] = {}


def register_transformation(name: str) -> Callable[[Callable[[], T]], Callable[[], T]]:
    """Decorator to register a transformation under a given name."""

    def decorator(factory: Callable[[], T]) -> Callable[[], T]:
        if name in _TRANSFORMATION_REGISTRY:
            raise ValueError(f"Transformation '{name}' already registered")

        _TRANSFORMATION_REGISTRY[name] = factory()
        return factory

    return decorator


def get_transformation_registry() -> dict[str, TransformationDefinition[Any]]:
    """Get the registry of built-in transformations."""
    return _TRANSFORMATION_REGISTRY.copy()
