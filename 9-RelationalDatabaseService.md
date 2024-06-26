# Relational Database Service

## Database Refresher and Models
Architectural fundamentals of Relational Database Systems
Relational (SQL) vs Non-Relational (NoSQL)
- Structured Query Language (SQL)- most use SQL and RDMS interchangably
- Structure *in* and *between* tables of data- rigid schema (defines names, valid values, fixed relationship between tables)
- NoSQL isn't one single thing... different models (lots of alternatives)
  - much more relaxed schema
  - relationships handled differently

Relational Database Management Systems (RDMS) example
- Table- Columnns (attributes), each row has a value
  - data that realtes together stored on a table
  - every row uniquely identifiable (primary key)
  - Human table and Animals table
- each table can have different attributes, but every row needs a value for every attribute
- define relationships between tables
  - join table- composite key (formed from two keys)
  - each animal can have multiple humans and each human can have multiple animals
  - schema is fixed and declared in advance
  - difficult with rapidly changing relationships

NoSQL databases (non-relational)
- Key-Value- list of key:value pairs, no structure or schema, scalable and fast
- Wide Column Store (variation of key:value)- 1 more more keys
  - Key1 (partition key), Key2 (sort/range key), keys unique to that table
  - attributes don't have to be the same between items (diff from SQL), mix and match attributes (any/all/none)
  - DynamoDB is Wide Column Store (perfect if relational operations not needed)
- Document- store and query data as documents
  - JSON or XML
  - each document interacted with as ID unique to that doc, "value" is contents of doc
  - Ideal scenario: interacting with whole documents or deep attribute interactions
- Column- most SQL DB are row based
  - ROW, Order ID, Product, Color, Size Price
  - read every row to find what you want, ideal if you are operating with rows
    - Online Transaction Processing (OLTP)- good for orders, contacts
  - COLUMN (Redshift)
    - data is same but grouped by column
    - very inefficient for transaction style processing
    - good for reporting r when all values for a specific attribute (size) are required
    - Readshift- take data from OLTP DB and shift to Column DB
  - Graph- relationships between things stored as part of DB
    - good for social media or HR
    - "edges" are relationsjip between "nodes"
    - can have attached data (:works_for->company also contains startdate:01/01/2001)
    - don't have to compute relations when query is run, relations are fluid and dynamic

## ACID vs BASE
DB Transaction Models
CAP Theorem- Consistency, Availability and Partition Tolerance
- Consistency- every read will receive most recent write
- Availability- every request receives non-error, but without guarantee to receive most recent write
- Partition Tolerance- system made of mult network partitions, operates even with dropped messages between nodes
- Choose 2 out of 3

ACID - Consistency (most common)
- Atomic- ALL or NO components of transaction SUCEEDS or FAILS
- Consistent- transactions move DB from one valid state to another, nothing in between
- Isolated- multiple transactions at once, they don't interefere with each other, each executes as if it's the only one
- Durable- once commited, transactions are durable. stored on non-volatile memory, resilient to power outages/crashes
- Exam- probably referring to RDS DB, limits scaling

BASE - Availability (scalable, high performance)
- BAsically available- R/W ops are available "as much as possible" but w/o consistency guarantee
- Soft state- DB doesn't enforce consistency, offloaded to app/user (data read might not be most recent written)
- Eventually consistent- wait long enough, reads will be consistent
- DynamoDB

Exam:
- BASE = NoSQL
- ACID = RDS
- NoSQL/Dynamo + ACID = probably DynamoDB Transactions

## Databases on EC2
Generally bad practice
EC2 Instance- Database/Application/Webserver OR DB on separate EC2 Instance (split architecture across 2 AZs)
- separating introcuces dependency- communication between app and DB, cost for data between AZs (same AZ comm is free)

Why you might do it...
- Access to the DB Instance OS (not typically really required)
- Advanced DP option tuning (DBROOT) - AWS might allow this control
- Vendor demands (app requirement), most vendors now support AWS DB products
- DB or DB version AWS don't provide
- Architecture AWS don't provide (replication/resilience)
- Decision makes who "just want it"

Why you shouldn't really...
- Admin overhead- managing EC2 and DBHost (patching, upgrading, staffinf outside normal hours)
- Backups/Disaster Recovery Management
- EC2 is *single AZ
- Features- some AWS DB products are very very good (don't want to miss out on features)
- EC2 is ON or OFF- no serverless, no easy scaling
- Replication- skills, time, monitoring, effectiveness
- Performance- AWS invest time into optimization and features

## Splitting Wordpress Monolith -> App and DB - DEMO
Move from Webserver0App-DB all on 1 EC2 -> Webserver-App + DB
Deploy stack... EC2... Instances...
Connect to Wordpress instance
- Commands:

```
# Backup of Source Database
mysqldump -u root -p a4lwordpress > a4lwordpress.sql


# Restore to Destination Database
mysql -h privateipof_a4l-mariadb -u a4lwordpress -p a4lwordpress < a4lwordpress.sql 

# Change WP Config
cd /var/www/html
sudo nano wp-config.php

replace
/** MySQL hostname */
define('DB_HOST', 'localhost');

with 
/** MySQL hostname */
define('DB_HOST', 'REPLACEME_WITH_MARIADB_PRIVATEIP'); 

sudo service mariadb stop
```
Copy backup for Wordpress DB to separate EC2 DB instance using its private IP
Configure WP to point at new DB server (edit wp-config.php)
Stop DB service on monolithic app

## Relational Database Service (RDS) Architecture
DBaaS product (not really, though)
DBServer-aaS
- multiple databases on one DB server (instance0)
- Choice of engines- MySQL, MariaDB, PostgreSQL, Oracle, MS SQL Server
- Amazon Aurora is a diff product
- Managed service- no access to OS or SSH 
- Runs in a VPC

US-EAST-1
  - 3 AZs + 2 DB Subnets (across all AZs)
    - AZA
    - AZB
    - AZC
    - RDS will put Primary and Standby DB in diff AZs
    - RDS can be accessed from VPC or over VPN
    - Can make DB instances public, but frowned upon
AP-SOUTHEAST-2

RDS instances can have multiple DB
Each has dedicated storage (EBS) per instance
Synchronous replication to standby as soon as data received
Asynchronous replication to Read Replicas (RRs) is an option
Backups and Snapshots to S3 (from standby instance)

Cost
- #1- Instance size and type (similar to EC2)
- #2- Multi AZ or not
- #3- Storage type and amount (per Gb)
- #4- Data transferred (per Gb)
- #5- Backups and Snapshots
- #6- Licensing (if applicable)

## Migrating EC2 DB into RDS - DEMO
Wordpress EC2
Wordpress DB EC2


Commands:
```
# Backup of Source Database
mysqldump -h PRIVATEIPOFMARIADBINSTANCE -u a4lwordpress -p a4lwordpress > a4lwordpress.sql


# Restore to Destination Database
mysql -h CNAMEOFRDSINSTANCE -u a4lwordpress -p a4lwordpress < a4lwordpress.sql 

# Change WP Config
cd /var/www/html
sudo nano wp-config.php

replace
/** MySQL hostname */
define('DB_HOST', 'PRIVATEIPOFMARIADBINSTANCE');

with 
/** MySQL hostname */
define('DB_HOST', 'REPLACEME_WITH_RDSINSTANCEENDPOINTADDRESS'); 
```
Install Wordpress and create a post, saves images to application and data to MariaDB instance
Open RDS AWS console...
- Create subnet group first... Create DB subnet group
  - Create in a4l-vpc (same as EC2)
  - Choose 3 AZs, then select database subnets in the VPC (open VPC in new tab to check IP address ranges for those subnets to pick the correct ones)
  - Subnet groups tell RDS what subnets to put DB into
- Create database (standard create)
  - Choose MySQL
  - Template- select Free Tier for our use (can't be multi-AZ)
  - DB instance identifier- unique (a4lwordpress)
  - Credentials, can choose username
  - Instance configuration- limited by free tier
  - Storage- Size and Type (Aurora doesn't need to preallocate storage)
    - Use min, 20 GiB, Disable autoscaling 
  - Connectivity, choose VPC and subnet group that was just created
  - Create new VPC security group
  - Additional configuration- define Initial database name (a4lwordpress)
  - Create, can take some time (up to 45 minutes)

- Every RDS isntance has Name and Port
- Open VPC security group that controls access to RDS instance
  - Edit, Add Rule allowing other instance to connect
  - Type:MYSQL/Auror, Instance:Select security group created by 1-click deployment
- Connect to EC2 Wordpress instance, reference commands above
  - Run mysqldump- backup source DB
  - Import backup file into new destination DB (RDS instance), need CName of instance (endpoint name)
  - Change wordpress song file to point to RDS instance (edit wp-config.php), change DB_HOST from EC2 instance to RDS DB name
  - Verify by open public IPv4 address of Wordpress instance, Stop EC2 DB instance (old DB), check if WP still works

## Relational Database Service (RDS) MultiAZ - Instance and Cluster
RDS- Multi AZ-Instance
- RDS has primary isntance, with multi AZ mode, replicates to another AZ (standby)
- method depends on DB engine- failover or mirroring; this is abstracted away
- Database CNAME points at primary instance- you always access primary
  - Backups can come from standby, placing no extra load on primary
  - Failure- DNS changes CNAME to point at standy RDS instance
- Data -> Primary AND replicated to Syandby = Commite (Synchronous)
- Not free tier
- ONE syandby replica ONLY
- ...which can't be used for reads or writes
- 60-120 seconds failover
- Same region only.... different AZs in the same region
- Failover- AZ outage, primary failure, instance type change, software patching

RDS- Multi AZ-Cluster
Similar to Aurora, but different
VPC over 3 AZs
- 1 Writer replicates to 2 Reader instances in 2 AZs, synchronous replication
  - Readers are usable
  - each instance has own local storage (different from Aurora)
    - Cluster endpoint- points at Writer, can be used for reads/writes or admin functions
    - Reader endpoint- any available reader, including the Writer
    - Instance endpoint, each gets one, not good to use directly (use for testing and fault-finding)
- 1 Writer and 2 Reader DB instances (different AZs)
- ...much faster hardware, Graviton + local NVME SSD storage
- ...fast writes to local storage -> flushed to EBS
- ...Readers can be used for reads...allowing some read scaling (Aurora can scale even more)
- Replication is via transaction logs... more efficient
- Failover is faster- ~35s + transaction log apply
- Writes are "commited" when 1 reader has confirmed

Cluster mode has benefits over Instance mode

## RDS Automatic Backup, RDS Snapshots, and Restore
Two types, both in S3 but buckets not visible in S3 console (regionally resilient):
- Automated Backups
  - once per day, but otherwise architecture same as snapshots
  - Backup window defined or selected auto by AWS
  - will be an I/O pause unless using multi-AZ
  - Every 5 minutes- Transaction logs to S3
  - Auto cleared, can set retention 0-35 days, older data removed
  - to maintain past retention period, create a final snapshot
- Snapshots
  - not automatic, function like EBS snapshots
  - taken of instance, not single DB
  - First snap is FULL, then only changes (incremental), first might take a while
  - Single AZ- might notice interruption; multi AZ- occurs on standby
  - Don't expire, live past deletion of RDS isntance
  - Manual, run at frequency you choose

Backups taken from standby instance (brief I/O pause)
RDS can replicate backups to another region (NOT default)... snapshots and transaction logs
  - Charges apply for cross-region data copy...and the storage in the destination region

RDS Restores
- Creates NEW RDS instance - new address
  - Must update applications with new address!
- Snapshots = single point in time, creation time
- Automate = any 5 minute point in time (minutes before failure)
- Backup is restored and transaction logs are 'replayed' to bring DB to desired point in time (Good RPO)
- Restores aren't fast- Think about RTO (*RR's)

## RDS Read Replicas
Performance benefits for reads, cross-region failover, low recovery time objectives (if no data corruption)

Read only replicas of RDS instance, can use but only for read operations
- not part of main DB instance, have own endpoint address
- App will have zero knowledge of replica by default, just exist off to one side
- Multi AZ uses Synchronous replication- data is replicated at same time its written to primary
- Asynchronous- primary first, then replicated to ReadReplicas
- RDS questions- Synchronous=MultiAZ, Asynchronous=ReadReplicas
- Can be created cross-region, AWS handles networking (transparently)

Read Performance Improvements
- 5x direct read-replicas per DB insatance
- each providing an additional instance of read performance
- Read-replicas can have read-replicas - but lag is a problem
- Global performance improvements, workloads can connect to RRs

RPO/RTO Improvement
- Snapshots and Backups improve RPO
- RTOs are a problem...
- RRs offer near zero RPO, little potential for data loss
- RRs can be promoted quickly- low RTO
- Recover from failure only- watch for data corruption
- Read only- until promoted, then use as normal RDS instance
- Global avilability improvements... Global resilience

## MultiAZ and Snapshot Restore with RDS - DEMO
Previously imported EC2 DB into RDS...
Create infrastructure with CF 1-Click...
Install Wordpress... Add new post... Go to RDS Console...

Snapshot: Select DB created by 1-click deployment... Take Snapshot...
  - creates full copy of data in DB instance
  - include DB version number in snapshot name
  - First snapshot is full, subsequent are incremental
  - Manual snapshots aren't handled by RDS

Replica- Multi AZ: Select DB... Modify...
  - Availability and durability... Create a standby instance... Can apply immediately or during next scheduled maintenance window
  - Automatic standby replica in another AZ, synchronously replicated, big advantage for primary performance, minimizes disruption
  - creates snapshot and retores to new AZ
  - Simulate a failure by selecting "reboot with failover", CNAME moved to point to standby replica (NOT immediate)

Restore is data corrupted
  - Change title of blog post... data "corrupted"
  - Go to snapshots... Select... Actions... Restore...
  - restoring creates new DB instance from snapshot
  - must update application to point at new DB (brand new CNAME)- update Wordpress settings

## RDS Data Security
Authentication and Authorization
- Local DB have usernames and PWs
- Can configure for IAM Auth
  - Start RDS instance, create local DB user configured to allow AWS auth token
  - IAM User or role has Policy attached, maps that IAM identity onto the local RDS user
  - token used to log in without password
  - ONLY authentication, not authorization, that's still controlled by local DB user

Encryption in transit
- SSL/TLS is avilable, can be mandatory
  
Encryption at rest
- RDS supports EBS volume encryption- KMS
- Handled by Host/EBS
- AWS or Customer Managed CMK generates data keys
- Storage, logs, snapshots, and replicas are encrypted
- ...encryption can't be removed
- RDS MSSQL and RDS Oracle support TDE
  - Transparent Data Encryption
  - Encryption handled with the DB engine (not by host)
- RDS Oracle supports integration with CloudHSM
- Much stronger key controls (even from AWS)

Amazon RDS KMS Encryption and TDS
- Host(Oracle, MySQL) -> CloudHSM
- TDE is native DB engine encryption, data encrypted before leaving the instance
- KMS provides AWS or Customer Managed CMKs which are used to generate Data Encryption Keys (DEKs) for RDS
  - DEKs loaded onto hosts as required

## RDS Custom
Not often used in real world
- Fills gap between RDS and EC2 running a DB engine
- RDS is fully managed- OS/Engine access limited
- DB on EC2 is self managed- but has overhead
- Works for MSSQL and Oracle
- Can connect using SSH, RDP, and Session Manager
- Injects elastic network interfaces into VPC, will see EC2 instance, backups
- RDS Custom *Database Automation* settings
  - ...pause (full automation) for normal production usage

On-prem DB- you are responsible for everything
RDS- AWS responsible for everything except Optimization
EC2- AWS handles hardware, you handle everything else
Custom- Hardware is AWS, Optimization it you, everything else (scaling, HA, backups, patches, OS install) shared

## Aurora Architecture
Part of RDS, but very unique product
Uses a "Cluster"- sinple primary instance + 0 or more replicas
  - replicas can be used for reads during normal operation
  - don't have to choose between read scaling and availability- Aurora replicas provide both
No local storage- uses cluster volume
  - faster provisioning and improved avialability

Functions across ultiple AZs
  - AZ-A- Primary
  - AZ-B- Replica
  - AZ-C- Replica
  - Cluster Volume: Max 128 TiB, 6 replicas, AZs
Primary is only instance that can write to storage, replicas read
When volume fails, Aurora repairs with data from other nodes
Can have up to 15 replicas and any can be failover target

All SSD Based- high IOPS, low latency
  - you don't specify storage, billed based on what's used
  - High water mark- billed for the most used
  - Storage which is freed up can be re-used
More recent versions of Aurora don't use "high water mark" architecture
Replicas can be added and removed without requiring storage provisioning

Endpoints- DNS addresses used to connect
  - Cluster Endpoint -> Primary instance
  - Reader Endpoint -> Primary instance + load balance to replicas
  - Can create custom endpoints

Cost
  - No free-tier option- doesn't support Micro Instances
  - Beyond RDS singleAZ (micro) Aurora offers better value
  - Compute- hourly charge, per second, 10 minute min
  - Storage- GB-Month consumed, IO cost per request
  - 100% DB size in backups are included

Restore, Clone, and Backtrack
  - Backups work same way as RDS
  - Restore creates a *new cluster*
  - Backtrack can be used which allow in-place rewinds to a previous point in time (enabled per cluster, can adjust window)
  - Fast Clones make a new database MUCH faster than copying all the data- copy-on-write (only stores data changed in the clone, minimal data use)

## Aurora Serverless
What Fargate is to ECS, removes admin overhead of managing instances
Aurora Provisioned vs Aurora Serverless
Scalable- ACU- Aurora Capacity Units
Aurora Serverless cluster has a Min and Max ACU
Cluster adjusts based on load
Can go to 0 and be paused
Consumption billing per-second basis
Same resilience as Aurora (6 copies across AZs)

Architecture
- Aurora Serverless Cluster
  - AZ-A- ACU (stateless, shared across many customers, allocated from pool)
  - AZ-B- ACU
  - AZ-C- ACU
  - more ACUs allocated as needed
  - Shared Proxy Fleet (Managed by AWS)
    - User -> Application -> Proxy Fleet instance -> ACU
    - scaling is fluid since you're not directly connecting with ACU

Use Cases
- Infrequently used applications
- New applications (create DB, scales based on incoming load)
- Variable workloads (scale based on demand)
- Unpredictable workloads
- Development and test databases (can pause itself when no load)
- Multi-tenant applications (scaling aligned with incoming revenue)

## Migrating to Aurora Serverless (SKIP) - DEMO

## Aurora Global Database
Allow you to create global level replication, master region -> up to 5 secondary regions
Primary region (us-east-1) Aurora cluster (1read/write, 15 read only replicas) -> Secondary region (ap-southeast-2) (16 read only replicas)
- ~1s replication

When to use:
- Cross-region DR (disaster recovery) and BC (business continuity)
- Global read scaling - low latency performance improvements
- ~1s or less replication between regions (one way form primary to secondary)
- no impact on DB performance (happens at storage layer)
- Secondary regions can have 16 replicas (all are read replicas)
- ...can be promted to R/W in disaster situation
- Currently MAX 5 secondary regions

## Aurora Multi-Master Writes
Allows Aurora to have multiple R/W instances (default is 1 writer, many readers)
Default: One R/W and 0+ Read Only Replicas
- Cluster endpoint is used to write, read endpoint is used for load balanced reads
- Failover takes time- replica promoted to R/W
- In multimaster mode *all instances are R/W*

Structure very similar to standard Aurora, but no cluster endpoint
- Application connects to one or all instances in cluster
- no load balanced endpoint
- when a R/W node receives write request, proposes data be commited to all storage nodes in that cluster
  - nodes can reject if another app is writing
  - writing instance looks for a quorum of nodes to agree, or rejects change with an error
  - replictes to every storage node in the cluster
  - With multi-master, replicated to other nodes in the cluster

Benefits
- Primary (R/W), 1 Replica (R/O)
- User -> Application -> Primary 
  - Primary fails, access is disrupted, change cluster endpoint to point to replica, this takes time
  - with multi-master, both instances are writers, app can connect with one or both
  - connection maintained if one fails
  - Multi-Master required for app to be "fault tolerant"

## Relational Database Service (RDS) - RDS Proxy
Why?
- Opening and closing DB connections consumes resources
- ...takes time, which creates latency
- with serverless... every lambda opens and closes?
- handling failure of DB instances is hard
- ...doing it within app addds risks
- DB proxies help... managing them is not trivial (scaling/resilience)
- Applications -> Proxy (connection pooling) -> DB

VPC1 (3 subnets in each AZ):
  - AZ-A - Catagram app
  - AZ-B - Primary RDS instance, Lambda ENI
  - AZ-C - Standby RDS instance, Catagram app
  - with RDS proxy, runs across all AZs, maintains Long Term Connection Pool to primary DB
  - clients (catagran EC2 instances) connect to proxy instead of directly to DB
  - Multiplexing is used so a small number of connections can be used for large number of clients
  - At failover, connection to standby takes place in the background

When to Use
- Too many connection errors
- DB instance using T2/T3 (i.e. smaller/burst) instance
- AWS Lambda... time saved/connection reuse and IAM Auth
- Long running connection (SAAS apps)- low latency
- Where resilience to DB failure is a priority
- ...and make it transparent to the application

Key Facts
- Fully managed DB proxy for RDS/Aurora
- ....auto scaling, highly available by default
- Provides connection pooling- reduces DB load
- ONLY accessible from a VPC (not public internet)
- Accessed via Proxy Endpoint- no app changes
- Can enforce SSL/TLS
- Can reduce failover time by over 60%
- Abstracts failure away from your applications

## Database Migration Service (DMS)
Managed service which allows for 0 data loss, low or 0 downtime migrations between 2 database endpoints
The service is capable of moving databases INTO or OUT of AWS

Runs replication instance (on EC2)
- define source and destination endpoitns point at...
- ...source and target DB
- One endpoint MUST be on AWS

Source (MySQL, Aurora, PostgreSQL, etc) -> Source Endpoint -> Replication Instance (running 1 or more replication tasks) -> Destination Endpoint -> Target
Jobs can be:
- Full load (if you can afford outage)
- Full load + CDC (change data capture)- full plus capture changes on source, applied after migration
- CDC only- replicate only changes, if you want to use an alternative method to transfer the bulk of the DB data, such as native tooling

Schema Conversion Tool (SCT)- schema conversions between diff DB versions or engines
- stand-alone application
- includes DB -> S3
- not used when migrating between DBs of the same type
  - on-prem MySQL -> RDS MySQL - not used
- works with OLTP DB types (MySQL, MSSQL, Oracle)
- ...and OLAP (Teradata, Oracle, Vertica, Greenplum)
- e.g. On-prem MSSQL -> RDS MySQL
- e.g. On-prem Oracle -> Aurora

DMS and Snowball
- Larger migrations might be multi-TB in size
- ...moveing over network takes time and consumes capacity
- Snowball products- bulk data transfer, uses SCT
- Step 1: Use SCT to extract data locally and move to snowball device
- Step 2: Ship device to AWS, they load to S3
- Step 3: DMS migrates from S3 into target store
- Step 4: Change Data Capture (CDC) can capture changes, and via S3 intermediary they are also written to the target DB
- DMS is used because you are moving to generic format for transfer

