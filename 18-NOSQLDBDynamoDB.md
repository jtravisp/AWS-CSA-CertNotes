# NOSQL Databases and DynamoDB

## DynamoDB - Architecture
DynamoDB is a NoSQL fully managed Database-as-a-Service (DBaaS) product available within AWS.

- NOSQL Public Database-as-a-service (DBaaS) - Key/Value and Document
- No self-managed servers or infrastructure
- Manual/Automatic provisioned performance IN/OUT or On-Demand
- Highly resilient... across AZs and optionally global
- Really fast... single digit milliseconds (SSD based)
- Backups, point in time recovery, encryption at rest
- Event-driven integration... do things when data changes

DynamoDB Tables
- A table is a grouping ot ITEMS with the same PRIMARY KEY
- An item is like a row in a traditional database
  - no limits to # of items
- Primary Key- Simple (Partition) or Composite (Partition and Sort)
  - every item uses same Primary Key
- Each item MUST have a unique alue for PK and SK, can have none, all, mixture, or different atrtributes
  - DDB has no rigid attribute schema
  - Item max 400KB
- Capacity (speed) is set on a table
  - Writes 1WCU = 1KB per second
  - Reads 1 RCU = 4KB per second

Backups
- On Demand (like manual RDS snapshots)- full, retained until you remove
  - Restore Same or cross-region
  - Restoe with or without indexes
  - Adjust encryption settings
- Point-in-time Recovery (PITR)
  - enable table by table, disabled by default
  - continuous stream of abckups, all changes over 35 day window
  - restore to within 1 second

Exam
- NOSQL? DynamoDB
- Relational Data... generally NOT DynamoDB
- Key/Value... prefer DynamoDB
- Access via console, CLI, API... 'NO SQL'
- Billed based RCU, WCU, Storage, and features, no infrastructure or base costs

## DynamoDB - Operations, Consistency, and Performance

Two Capacity Modes
- On-Demand- unknown, unpredictable, low admin
  - price per million R or W units
  - paying more
- Provisioned... RCU and WCU set on per table basis (Read Capacity Units/Write Capacity Units)
- Every operation consumes at least 1 RCU/WCU
- 1 RCU is 1 x 4KB read operation per second (operations round up)
- 1 WCU is 1 x 1KB write operation per second
- Every table has a RCU and WCU burst pool (300 seconds)

Query
- retrieve data
- have to specify single value for partition key
- Query accepts a single PK value and optionally a SK or range
- Capacity consumed is the size of all returned items
- Further filtering discards data- capacity is still consumed
- Can ONLY query on PK or PK and SK
- e.g. weather station data
  - Query (PK=1), 2 items returned
    - Total data = 4K = 1RCU
    - every operation consumes at least 1 RCU, pull as much as possible/needed per query
  - Query (PK=1,Day=MON)
    - Capacity consumed 2.5K = 1 RCU
- Query only ever quesries on 1 Partition Key value

Scan
-least efficient operation for getting data, most flexible
- e.g. weather station data
  - Scan moves through tabel item by item
- complete control on what data is selected, any attributes can be used and any filters applied, but SCAN consumes capacity for everyITEM scanned through
- e.g. Scan for all items in all weather stations for "sunny day"
  - can't use Query- only allows 1 value of PK, need to look across all
  - doesn't return non "sunny day" but still consumes entire capacity because extra data is discarded

Consistency Model
- Consistency- new data written and read, is read data same as update or only eventually the same?
- DynamoDB- every piece of data replicated multiple times in separate AZs
  - every point - Storage Node, one is "leader"
  - AZA, AZB, AZC, Leader = AZB
  - Bob updates a DynamoDB Item, removing an attribute, Writes are always directed at Leader Node
  - Leader is now "consistent", Writes don't scale as well as reads
  - The Leader Node replicates data to other nodes, typically finishing within a few milliseconds
  - maybe AZC get write before AZA
    - Eventually Consistent Reads are 1/2 price of Strongly Consistent Reads
  - Julie performs eventually consistent read of data, DDB directs her to 1 of 3 nodes at random
    - most cases all3 will be same
    - in this case, AZA is slightly behind, "stale"
    - in most cases, will notice no difference
    - Strongly Consistent Read always uses Leader Node
  - Not every application or access type tolerates Eventual Consistency (medical applications), select the appropriate model

WCU Calculation
- need to store 10 items every second... 2.5K avg size per item
- Exam gives you items/minute? Calculate per second since that's how WCU/RCU determined
- Calculate WCU per item... ROUND UP (ITEM / 1KB) = 2.5 rounded up to 3
  - Multiply by average number per second- 10/s x 3 = 30 WCU required

RCU Calculation
- retrieve 10 ITEMS per scond... 2.5K average
- (ITEM SIZE / 4KB) = 4/2.5 is < 1, so round up to 1
- Multiply by avg read ops per second (10)
- =Strongly Consistent RCU Required = 10 RCU
- Eventually Consistent? 1/2 price, so 5 RCU

## DynamoDB Local and Global Secondary Indexes

- Query is the most efficient operation in DDB
- Query can only work on 1 PK value at a time
- ...and optionally a single, or range of SK values
- Indexes are alternative views on table data
- Different SK (LSI) or Different PK and SK (GSI)
- Some or all attributes (projection)

Local Secondary Indexes (LSI)
- an alternative view for a table
- MUST be created with a table
- 5 LSIs per base table
- Alternative Sort Key (SK), but same Partition Key (PK)
- Shares RCU and WCU with the table
- Attributes- ALL, KEYS_ONLY, and INCLUDE
- Example
  - weather station data
  - WeatherStation#, Day
  - want to use "Sunny Day", can't Query, Scan is inefficient
  - while creating table, create LSI using "Sunny Day" as alternate Sort Key
  - only values with new sort key are present in index, so only sunny days
    - only consume capacity for data that is relevant

Global Secondary Indexes (GSI)
- can be created at any time
- default limit of 20 per base table
- Alternative PK and SK
- GSIs have their own RCU and WCU allocations
- Attributes- ALL, KEYS_ONLY, and INCLUDE
- Example
  - weather station data
  - items that include Alarm when data taken
  - couldn't use Query, would need to use Scan and filter by Alarm attribute, scans every item
  - instead create GSI, alternative PK and SK
  - Alarm ID as PK and station ID as SK
  - alternative perspective on data in table
- GSIs are sparse, only items which have values in the new PK and optional SK are added
- GSIs are always eventually consistent, replication between base and GSI is asynchronous

Exam
- Careful with projection (KEYS_ONLY, INCLUDE, ALL)
  - project all attributes into index, using all capacity of those attributes
  - inverse is not projecting specific attribute, then requiring it later, very inefficient/expensive
- Use GSIs as default, LSI only when strong consistency is required
- Use indexes for alternative access patterns

## DynamoDB - Streams and Lambda Triggers

DynamoDB Streams are a 24 hour rolling window of time ordered changes to ITEMS in a DynamoDB table

Streams have to be enabled on a per table basis , and have 4 view types
- KEYS_ONLY
- NEW_IMAGE
- OLD_IMAGE
- NEW_AND_OLD_IMAGES

Lambda can be integrated to provide trigger functionality - invoking when new entries are added on the stream.

Stream Concepts
- Time ordered list of ITEM CHANGES in a table
- 24-hour rolling window
- Enabled on a per table basis
- Records INSERTS, UPDATE, and DELETES
- Different view types influene what is in the stream
- Table- 1 item
  - item changed, 4th attribute removed
  - Stream- KEYS_ONLY (records partition key, not how manipulated), NEW_IMAGE (entire item with state after change), OLD_IMAGE (copy of data before change), NEW_AND_OLD_IMAGES (both old and new)
- all views work with inserted or deleted items, but pre or post change might be empty

Trigger Concepts
- Streams are foundation, actions in event of change in data
- ITEM changes generate and event
- Event contains the data which changed
- An action is taken using that data
- AWS = Streams + Lambda
- used in Reporting and Analytics scenarios
- used in Aggregation, Messaging, or Notifications

- Table- ITEM change occurs
  - Stream record is added onto Stream
  - NEW_AND_OLD_IMAGES -> Lambda function

## DynamoDB - Global Tables
DynamoDB Global Tables provides multi-master global replication of DynamoDB tables which can be used for performance, HA or DR/BC reasons.

- Global tables provides multi-master cross-region replication
- Tables are created in mlutiple regions anda dded to the same global table (becoming replica tables)
- Last writer wins is used for conflict resolution (cimple with predictable outcomes)
  - DDB picks most recent write and overwrites everywhere else
- Reads and Writes can occur to any region
- Generally sub-second replication between regions
- Strongly consistent Reads ONLY in the same region as writes
  - anything else Eventual Consistency, Global apps need to be able tolerate this
  - can't cope? global tables will be a problem

- To use: select regions that will be part of global table
  - e.g. us-east, london, australia
  - from table in US, add tables into global table config, will establish global replication
- Sub-second replication between table replicas
- Mulit-master replication, all tables can be used for Read and Write operations
- Provides Global HA and Global DR/BC (Disaster Recover/Business Continuity)

## DynamoDB - Accelerator (DAX)
DynamoDB Accelerator (DAX) is an in-memory cache designed specifically for DynamoDB. It should be your default choice for any DynamoDB caching related questions.

- substantially improves performance, part of the product

Traditional Caches vs DAX
- Application using DDB
  - checks cache for data- a CACHE MISS occurs if data isn't cached
  - Data is loaded from the DB with a separate operation and SDK
  - Cache is updated with retrieved data, subsequent queries will load data from cache as a CACHE HIT
  - lacks integration with DB
- Application using DDB w/ DAX
  - DAX SDK <-> DDB
  - App uses the DAX SDK and makes a single call for the data which is returned to DAX
  - DAX either returns the data from its cache or retrieves it from the FB and then caches it
- DAX = less complexity for the app developer - tighter integration

DAX Architecture
- operates in a VPC, deployed into multiple AZs tn ensure HA
- Primary Node - R/W node
  - Read Replica Nodes - DAX-RR in different AZs
- Caches:
  - Item Cache holds results of (Batch)GetItem. 
  - Query cache olds data based on query/scan parameters
- DAX is accessed via and endpoint
  - Cache HITS are returned in microseconds... MISSES in milliseconds
- Write-Through is supported, data is written to DDB then DAX
- If a CACHE MISS occurs data is also written to the primary node of the cluster

DAX Considerations
- Primary NODE (Writes) and Replicas (Read)
- Nodes are HA... Primary Failure = election and fail-over to replica
- In-Memory cache - Scaling... much faster reads, reduced costs
- Scale UP and Scale OUT (Bigger or More)
- Supports Write-Through, DAX handles data being commited to DDB and storing in cache
- DAX deployed withing a VPC, app must also be in VPC
- reading same data over and over? DAX
- DAX has lower admin overhead than traditional cache
- Strongly consistent reads required? Don't use DAX

## DynamoDB - TTL
Amazon DynamoDB Time to Live (TTL) allows you to define a per-item timestamp to determine when an item is no longer needed. Shortly after the date and time of the specified timestamp, DynamoDB deletes the item from your table without consuming any write throughput. TTL is provided at no extra cost as a means to reduce stored data volumes by retaining only the items that remain current for your workload’s needs

- Table with Partition Key (PK) and Sort Key (SK)
  - also 3 attributes
- TTL defines timestamp, when an item is no longer required
- at that date/time, item deleted
- Enable TTL and choose specific attribute
- When configured, configs automated processes, preiodically scans, checks current time (in seconds since epoch) to the value in the TTL attribute
- ITEMS where the TTL attribute is older than the current time are set to Expired
- Another per-partition background process scans for expired items and removes them from tables and indexes and a delete is added to streams if enabled
- A Stream of TTL deletions can be enabled (24 hour window)
- Useful for regulatory or contractual needs

## Amazon Athena
Amazon Athena is serverless querying service which allows for ad-hoc questions where billing is based on the amount of data consumed.
Athena is an underrated service capable of working with unstructured, semi-structured or structured data.

- Serverless Interactive Querying Service
- Ad-hoc queries on data (S3)- pay only data consumed, no base cost or per minute
- Schema-on-read - table-like translation
- Original data never cahnged - remains on S3
- Schema translates data -> relational-like when read
  - normally data must be in format of tables, not required with Athena
- Output can be sent to other services

Architecture
- Source Data (S3)
  - Athena can directly read many AWS data formats: XML, JSON, CSV, AVRO, PARQUET, ORC, Apache, CloutTrail, VPC Flowlogs
  - supports standard formats of structured, semi-structured, and unstructured data
- SCHEMA
  - Define tables inside, source data -> table like structure, run queries against tables
  - tables don't actualy contain data, contain directives on how to convert source data
  - "Tables" are defined in advance in a data catalog and data is projected through when Read
    - allows SQL-like queries on data without transforming source data
- Billed based on data consumed during query

Athena
- no infrastructure, don't need to load data in advance
- Great on Queries where loading/transformation isn't desired (large data sets)
- Great for Occasional/Ad-Hoc queries on data in S3
- Great for serverless querying scenarios - cost conscious
- preferred solution- AWS Service Logs - VPC Flow Logs, ClouTrail, ELB logs, cost reports, etc.
- AWS Glue Data Catalog and Web Server Logs
- Athena Federated Query... non S3 data sources
  - most situations- SQL, NOSQL- answer likely not Athena

## Athena - DEMO
Planet OSM - ioen set of data maintained and delivered as a set of alrge data files- not structured into tables
3 files
    - planet
    - planet_history
    - changesets
- will use planet file, very large
- with Athena, us Open Street Map data as source (>100GB)
- define Scheme, don't modify original data, data is read into Athena, presented in tables

- create area of nterest with GPS coordinates
  - use this to make a query
  - generate output data, vaccination vets in the area

- Athena console, Query editor
  - create bucket for output of results in S3; Athena: Settings, Manage
  - Editor tab
  - use commands below, new query window for each set of commands
- Test Query loads data from source location (s3://osm-pds/planet/) through table
- Query an area of interest using latitude and longitute, use Google Earth to get coordinates
  - Run query, will scan huge amount of data, produces list of vets in area specified
- When done, drop databases

```
# Create the Athena DB
CREATE DATABASE A4L;


# Create the Athena DB Table, not loading any data yet

CREATE EXTERNAL TABLE planet (
  id BIGINT,
  type STRING,
  tags MAP<STRING,STRING>,
  lat DECIMAL(9,7),
  lon DECIMAL(10,7),
  nds ARRAY<STRUCT<ref: BIGINT>>,
  members ARRAY<STRUCT<type: STRING, ref: BIGINT, role: STRING>>,
  changeset BIGINT,
  timestamp TIMESTAMP,
  uid BIGINT,
  user STRING,
  version BIGINT
)
STORED AS ORCFILE
LOCATION 's3://osm-pds/planet/';

# Test Query

Select * from planet LIMIT 100;

# Locational Query

SELECT * from planet
WHERE type = 'node'
  AND tags['amenity'] IN ('veterinary')
  AND lat BETWEEN -27.8 AND -27.3
  AND lon BETWEEN 152.2 AND 153.5;
```

## Elasticache
Elasticache is a managed in-memory cache which provides a managed implementation of the redis or memcached engines.
Its useful for read heavy workloads, scaling reads in a cost effective way and allowing for externally hosted user session state.

- In-memory database... high performance
  - disk will always be subject to performance limits, memory is faster
- Managed Redis or Memcached... as a service
- Can be used to cache data - for READ HEAVY workloads with low latency requirements
- reduces DB workloads (expensive)
- can be used to store Session Data (Stateless Servers)
- Requires application code changes!!!
  - app needs to know to check cache for data

Architecture
- Aurora backend DB with Elasticache
- App -> Elasticahce for data, CACHE MISS
  - App -> DB (slower and more expensive) -> writes data to cache
  - next time App -> Elasticache, CACHE HIT
- over time, many more CACHE HITS
- allows cost effective scaling of read0heavy workloads - and performance improvement at scale

Session State Data
- ASG - 3 EC2 instances, load balancer -> Persistent Data -> Aurora
- Use Elasticache to store session data
  - User -> instance -> Elasticache session state written
    - Instance fails? connection moved to another isntance by load balancer
    - Session State loaded from cache, session continues with no interruption
    - Fault-Tolerant application
- Two diff engines:
  - Redis
  - MemcacheD

Redis vs MemcacheD
- both sub millisecond access, range of programming languages
- MemcacheD
  - Simple data structures
  - no replication
  - Multiple nodes (sharding)
  - No backups
  - Multi-threaded by design
- Redis
  - Advanced structures (e.g. game leader board sorted by rank)
  - multi-AZ replication
  - Replication (Scale reads)
  - Backup and restore
  - Transactions- multiple operations as one (all or none work)- good for more strict consistency requirements
- Multi AZ or other HA/resilience? select Redis

## Redshift Architecture
Redshift is a column based, petabyte scale, data warehousing product within AWS
Its designed for OLAP products within AWS/on-premises to add data to for long term processing, aggregation and trending.

- Petabyte-scale data warehouse (long-term analysis and trending)
- OLAP (online analytical processing) (Column based), not OLTP (online transction processing) (row/transaction) - e.g. adding orders to online store
  - column bases- reporting style queries easier and more efficient to process
- Pay as you use... similar structure to RDS
- Direct Query S3 using Redshift Spectrum
- Direct Query other DBs using federated query
- Integrates with AWS tooling such as Quicksight
- SQL-like interface JDBC/ODBC standards connections

Architecture
- Server based (not serverless like Athena), has a provisioning time (no ad-hoc)
- Cluster architecture- private network
  - One AZ in a VPC - network cost/performance (not HA by design)
- Leader Node- Query input, planning, and aggregation- manages communications with client programs
- Compute Node- performing queries of data assigned by Leader Node
  - partitioned into Slices
  - each slice has portion of memory and disk space
  - Leader Node apportions workload onto slices
  - Slices work in parallel
  - Node might have 2, 4, 16, 32 slices
- VPC Security, IAM Permissions, KMS at rest encryption, CW monitoring
- Redshift Enhanced VPC routing feature - VPC Networking!!
  - default - public routes for traffic
  - Enhanced VPC routing- traffic routed based on VC networking config (Security groups, network ACLs, etc)
  - Any custom network requirements? Enable!!!

- VPC - Subnet in 1 AZ - RedShift Cluster
  - Leader Node <-> Apps, anything outide cluster (JDBC/ODBC compatible connections)
  - Nodes have Slices
  - Data is replicated to 1 additional node
- Automatic cnapshots to S3 (8 hours, 5GB) with retention
- Manual snapshots to S3... managed by admin
- Cnapshots configured to copy to another AWS region
- Can load data from S3, COPY from DynamoDB, Firehose can stream data into Redshift, DMS can migrate data in

## Redshift DR and Resilience
Backup options for redshift to overcome the single AZ risk.

Redshift - 1AZ
Resilience and Recovery
- AZA and AZB - Redshift in AZB
- AZB might fail
- S3 Snapshot Backups
  - Auto incremental every 8 hours or 5GB of data and by default have 1-day retention (config up to 35 days
  - Manual snaps can be taken at any time - and deleted by an admin as required
  - Redshift backups into S3 protect against AZ failure
  - can configure snapshots to be copied to another region, data safe from entire region failure
    - separate configurable retention period
