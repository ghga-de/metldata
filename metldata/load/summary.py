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

"""Generate global summary statistics."""

from typing import Any, Optional

from ghga_service_commons.utils.utc_dates import now_as_utc

from metldata.artifacts_rest.models import ArtifactInfo
from metldata.load.aggregator import DbAggregator

SUMMARY_COLLECTION_NAME = "summary"


def get_stat_slot(resource_class: str) -> Optional[str]:
    """Get the name of the slot that shall be used as grouping key."""
    if resource_class.endswith("File"):
        return "format"
    if resource_class.endswith("Protocol"):
        return "type"
    if resource_class.endswith("Individual"):
        return "sex"
    return None


async def create_summary_using_aggregator(
    artifact_infos: dict[str, ArtifactInfo],
    db_aggregator: DbAggregator,
) -> None:
    """Create summary by running an aggregation pipeline on the database."""
    summary: dict[str, Any] = {}
    last_artifact_info = next(reversed(artifact_infos.values()))
    last_artifact_name = last_artifact_info.name
    for resource_class in last_artifact_info.resource_classes:
        collection_name = f"art_{last_artifact_name}_class_{resource_class}"

        pipeline: list[dict[str, Any]] = [{"$count": "count"}]
        result = await db_aggregator.aggregate(
            collection_name=collection_name, pipeline=pipeline
        )
        if not result:
            continue
        summary[resource_class] = result[0]

        stat_slot = get_stat_slot(resource_class)
        if not stat_slot:
            continue

        pipeline = [{"$group": {"_id": f"$content.{stat_slot}", "count": {"$sum": 1}}}]
        result = await db_aggregator.aggregate(
            collection_name=collection_name, pipeline=pipeline
        )
        if not result:
            continue

        stats = {group["_id"]: group["count"] for group in result}
        summary[resource_class]["stats"] = {stat_slot: stats}

    if summary:
        summary.update(_id="global", created=now_as_utc())
        await db_aggregator.write(
            collection_name=SUMMARY_COLLECTION_NAME, document=summary
        )