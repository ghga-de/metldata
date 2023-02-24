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

"""Logic for handling reference paths."""


class ReferencePath:
    """A model describing the path of a reference between classes of a metadata model.

    The reference path has two available representation. A string-based ("path_str"
    attribute) and an element-based ("elements" attribute) one.

    In the string-based representation ("path_string" attribute), the first and the last
    word correspond the name of the source and target class, respectively. ">" and "<"
    means indicate active (left class references the right one) and passive (the left
    class is referenced by the right one). Parentheses attached to these angles thereby
    indicate the slot name of the referencing class. E.g. "class_a(has_class_b)>class_b"
    means that the source class "class_a" has a slot "has_class_b" that references the
    target class "class_b". Or "class_a<(has_class_a)class_b" means that the source
    class "class_a" is reference by the target class "class_b" via its slots
    "has_class_a". Reference paths can also involve additional classes. E.g. a string of
    "class_a<(has_class_a)class_b(has_class_c)>class_c" means that
    a reference from the source class "class_a" to the target class "class_c" can be
    established via an additional class "class_b". Any inserted spaces or newlines will
    be ignored. So the following paths are equivalent:
        - "class_a (has_class_b)> class_b"
        - "class_a
            (has_class_b)>
            class_b"

    A reference path consists of one or more elements. An element is a relationship
    between two classes. Reference paths that establish a direct relationship between
    source and target classes without the use of additional classes have only one
    element (e.g. in string reprentations "class_a(has_class_b)>class_b" or
    "class_a<(has_class_a)class_b"). More complex paths consist of multiple elements.
    E.g. the path "class_a<(has_class_a)class_b(has_class_c)>class_c" can be decomposed
    into the elements: "class_a<(has_class_a)class_b" and
    "class_b(has_class_c)>class_c".

    The elements of a ReferencePath are stored in the "elements" attribute as a list
    of ReferencePathElement objects that are optimized for programmatic use.
    """

    def __init__(self, path_str: str):
        """Construct reference path from a string based representation."""
