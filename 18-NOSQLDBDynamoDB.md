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


## DynamoDB - Accelerator (DAX)


## DynamoDB - TTL


## Amazon Athena


## Athena - DEMO


## Elasticache


## Redshift Architecture


## Redshift DR and Resilience



