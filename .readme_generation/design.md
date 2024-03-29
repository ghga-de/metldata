The framework uses a combination of ETL, CQRS, and event sourcing. Currently it is
designed to mostly run as a CLI application for managing metadata on the local file
system. However, later, it will be translated into a microservice based-architecture.

### One Write and Multiple Read Representations

Instead of having just a single copy of metadata in a database that
supports all CRUD actions needed by all the different user groups, we
propose to follow the CQRS pattern by having one representation that is
optimized for write operations and multiple use case-specific
representations for querying metadata. Thereby, the write-specific
representation is the source of truth and fuels all read-specific
representations through an ETL process. In the following, the
read-specific representations are also referred to as artifacts.

This setup with one write and multiple read representation has the
following advantages:

- Different subsets of the entire metadata catalog can be prepared
  with the needs and the permissions of different user audiences in
  mind.
- It allows for independent scalability of read and write operations.
- The metadata can be packaged in multiple different formats required
  and optimized for different technologies and use cases, such as
  indexed searching with ElasticSearch vs. REST or GraphQL queries
  supported by MongoDB.
- Complex write-optimized representations, which are inconvenient for
  querying such as event histories, can be used as the source of
  truth.
- Often used metadata aggregations and summary statistics can be
  precomputed.
- Read-specific representations may contain rich annotations that are
  not immediately available in the write-specific representation. For
  instance, the write-specific representation may only contain one-way
  relationships between metadata elements (e.g. a sample might define
  a `has_experiment` attribute, while an experiment defines no
  `has_sample` attribute), however, a read-specific representation may
  contain two way relationships (e.g. a sample defines a
  `has_experiment` attribute and an experiment defines a `has_sample`
  attribute).

However, there are also disadvantages that are linked to this setup that
should be considered:

- The write and read representations are only eventually consistent.
- Adds more complexity than a CRUD setup.

### Submission-centric Store as The Source of Truth

In the write-specific representation, metadata is packaged into
submissions. Each submission is fully self-contained and linking between
metadata of different submissions is not possible. A submission can have
one of the following statuses:

- pending - the construction of the submission is in progress, the
  submitter may still change its content.
- in-review - the submitter declared the submission as complete and is
  waiting for it to be reviewed, however, both the submitter and the
  reviewer can set this submission back to pending to enable further
  changes.
- canceled - the submission was canceled before its completion, its
  content was deleted.
- completed - the submission has been reviewed and approved, the
  content of the submission is frozen, and accessions are generated
  for all relevant metadata elements.
- deprecated-prepublication - the submission was deprecated and it
  cannot be published anymore, however, its content is not deleted
  from the system.
- emptied-prepublication - the submission was deprecated and its
  content was deleted from the system, however, the accessions are not
  deleted.
- published - the submission was made available to other users.
- deprecated-postpublication - the submission was deprecated and it
  should not be used anymore, however, its content stays available to
  other users.
- hidden-postpublication - the submission was deprecated and its
  content is hidden from other users but it is not deleted from the
  system, the accessions stay available, the submission can be set to
  deprecated to make its content available again.
- emptied-postpublication - the submission was deprecated and its
  content was deleted from the system, however, the accessions stay
  available.

The following status transitions are allowed:

- pending -\> in-review
- pending -\> canceled
- in-review -\> completed
- in-review -\> canceled
- in-review -\> pending
- completed -\> published
- completed -\> deprecated-prepublication
- completed -\> emptied-prepublication
- deprecated-prepublication -\> emptied-prepublication
- published -\> deprecated-postpublication
- published -\> hidden-postpublication
- published -\> emptied-postpublication
- deprecated-postpublication -\> hidden-postpublication
- deprecated-postpublication -\> emptied-postpublication
- hidden-postpublication -\> deprecated-postpublication
- hidden-postpublication -\> emptied-postpublication

A deprecated submission may or may not be succeeded by a new submission.
Thereby, the new submission may reuse (a part of) the metadata from the
deprecated submission. The reused metadata including the already
existing accessions is copied over to the new submission so that the
contents of the deprecated submission and the new submission can be
handled independently, for instance, the deprecated submission being
emptied.

### Event Sourcing to Generate Artifacts

To implement the ETL processes that generate read-specific artifacts
from the write-specific representation explained above, we propose an
event-sourcing mechanism.

The creation and each status change of a given submission (and
accommodating changes to the submission\'s content) are translated into
events. The events are cumulative and idempotent so you only have to
consume the latest event for a given submission in order to get the
latest state of that submission and a replay of the events will lead to
the same result. Thus, the event history only needs to keep the latest
event for each submission as implemented in the compacted topics offered
by Apache Kafka.

Moreover, since submissions are self-contained and do not depend on the
content of other submissions, events of different submissions can be
processed independently.

Multiple transformations (as in the ETL pattern) are applied to these
so-called source events to generate altered metadata representations
that are in turn published as events. These derived events can be again
subjected to further transformations.

Finally, the derived events are subject to load operations (as in the
ETL pattern) that aggregate the events and bring them into queryable
format (an artifact) that is accessible to users through an API.

### Metadata Modeling and Model Updates

Metadata requirements are modeled using LinkML. Thereby, the metadata
model should take the whole metadata lifecycle into account so that it
can be used to validate metadata before and after the submission as well
as for all derived artifacts.

Updates to the metadata model are classified into minor and major ones.
For minor updates, existing submissions are automatically migrated. The
submission always stores metadata together with the used metadata model.
The migration is realized through scripts that migrate metadata from an
old version to a newer version. Multiple migration scripts may be
combined to obtain a metadata representation that complies with the
newest version. The migration can be implemented as a transformation
that is applied to the source events as explained above.
