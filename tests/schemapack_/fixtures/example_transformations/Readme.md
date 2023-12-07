<!--
 Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
 for the German Human Genome-Phenome Archive (GHGA)

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

-->

This directory contains test cases for testing builtin transformation.

Names of sub-directories correspond to the transformation names.
Each sub-sub-directory represents a test case.
A test case is defined by following four files:
- `config.yaml` - the transformation config
- `input.datapack.yaml` - the input data for this transformation, if not present,
  the [../example_data/advanced.datapack.yaml](../example_data/advanced.datapack.yaml)
  is used
- `input.schemapack.yaml` - the model for the input data, if not present,
  the
  [../example_models/advanced.schemapack.yaml](../example_models/advanced.schemapack.yaml)
  is used
- `transformed.datapack.yaml` - the expected data output of the transformation
- `transformed.schemapack.yaml` - the expected model output of the transformation
