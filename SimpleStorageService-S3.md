# S3

## S3 Security (Resource Policies and ACLs)
S3 is private by default
    - only identity with initial access is account root user, all other permissions explicitly granted
  
S3 Bucket Policy
    - resource policy
      - like identity policy, but attached to bucket
      - can allow access from other accounts
      - allow/deny anonymous principals
 Bucket: secretcatproject
    - attached: Bucket Policy
    `"Principal": "*",`
        - defines who statement applies to, not in identity policy (because it by definition applies to that user)
        - * means policy applies to anyone accessing bucket, can perform defined action
        - can only have one bucket policy, with many statements

Access Control Lists (ACLs)- on objects or buckets
    - Subresource
    - Legacy (use policies instead)
    - Inflexible, simple permissions

Block Public Access
    - Resource Permissions- public could access bucket with no restrictions if turned on
    - AWS added Block public access settings
    - Failsafe

### Which policy?
Identity: controlling diff. resources
Identity: you have a preference for IAM
Identity: same account
Bucket: just controlling S3
Bucket: anonymous or cross-account
ACLs: never- unless you must

## S3 Static Hosting
Accessing S3 is generally done via APIs
- secure, flexible

Static website hsoting- access via HTTP
Enable
- set Index (what you get when you don't specify a page) and Error documents
- Website Endpoint created (name influenced by bucket name and endpoit, auto generate)
    - can only use custom domain name IF bucket name matches domain name

Scenarios
- Offloading
  - e.g. top10.animals4life.org
  - dynamic (needs DB)?- not suitable for S3
  - static media? perfect!
  - move media/images to S3 with static hosting enabled
  - much cheaper than storing in compute service
- Out-of-band pages
  - e.g. show maintenance page from separate server
  - another service, change DNS and point customers to nackup site on S3

Pricing
- cost to store, per GB/month
- data transfer
  - data in always free
  - data out, per GB
- requesting data (every GET, LIST, PUT, etc)
  - cost per 1,000 operations
  - if use is heavy might use lots of requests
- Free
  - 5GB storage monthly
  - 20k GET and 20K PUT requests

## S3 Static Site Demo

## Object Versioning and MFA Delete
- versioning starts disabled, after enabling, CAN'T disable (but can suspend)

Versioning
- store multiple versions of an object in a bucket
- if disabled, id=null
- enabled, id allocated
- each version of an object retained, but with differents IDs
- if version ID not specified, most recent (current) version returned
- delete? Delete Marker created (really just hidden)
  - delete the Delete Marker = restore object
  - if you specify version ID when delete, really deletes object
- CAN'T be switched off, all different versions take up space

MFA Delete
- enabled in versioning config
- MFA required to change bucket versioning state or delete versions
- Serial number (MFA) + Code passed with API calls

## Demo - S3 Versioning

## S3 Performance Optimization
Uploads to S3- Put Object API call (s3:PutObject), single data stream
- stream fails- entire upload fails, requires full restart
- single stream is slow and unreliable
  
Multipart Upload
- break data up into parts
- minimum size - 100MB
- almost no situations where single Put is worth it
- max 10,000 parts, 5MB -> 5GB each (last part can be smaller)
- parts can fail and be re-started
- Overall transfer rate is sum of parts, overcomes single stream limitations, more effectively use internet bandwidth

S3 Transfer Acceleration
- S3 is regional
- no control over public internet data path (never optimal)
- Transfer acceleration uses AWS edge locations
  - default is switched off
  - bucket name can't contain periods, needs to be DNS compatible in naming
  - data immediately enters closes edge location (geographically much closer than going across the world)
  - direct links from edge locations to AWS region
  - benefits improve as distance increases

## Demo - S3 Performance
S3 Console, create bucket (no periods)
Bucket properties... enable Transfer Acceleration... provides NEW endpoint for bucket that resolves to edge location
[AWS Accelerated Transfer Tool](http://s3-accelerate-speedtest.s3-accelerate.amazonaws.com/en/accelerate-speed-comparsion.html)
Benefits change with region

## Key Management Service (KMS)
Create and manage cryptographic keys and control their use across a wide range of AWS services
Regional and public

- Create, Store, Manage
- Symmetric and Asymmetric
- Cryptogtaphic operations (encrypt, decrypt, etc)
- Keys *never* leave KMS - provides *FIPS 140-2 (L2)* compliance
  - some features have achieved L3 compliance, overall L2

KMS Keys (used to be CMKs)
- logical, container for key material
  - ID, date, policy, description, state
  - backed by physical key material
  - Generates OR Imported
  - can be used for up to 4KB of data

- Create KMS key
  - stored encrypted on disk
  - request data encrypted- make Encrypt call to KMS, KMS decrypts key, uses key to encrypt data
  - Decrypt- make Decrypt call to KMS, KMS decrypts key, decrypts data, returns in plaintext
  - keys *never* leave KMS
- Permissions are granular

Data Encryption Keys (DEKs)
- GenerateDataKey - works on > 4KB
- created from KMS keys
- KMS doesn't store DEKs in any way, uses and discards- you or services actually uses the key
DEK generated:
- Plaintext version of key (to be used immediately, then discard) AND 
- Ciphertext version (store with encrypted data)
- DEK encrypted using KMS key that generated it
- Always have correct key since it's stored with encrypted data (but DEK and data are both encrypted)

S3 generates DEK for every object 

### Key Concepts
KMS keys are isolated to region and never leave (cannot extract)
Multi-region keys supported
Keys are AWS owned or Customer owned
  - Customer Owned- AWS Managed or Customer Managed
  - Customer managed = more configurable
KMS keys support rotation (can't be disabled with AWS managed)
Contains Backing Key (and previous backing keys)
Aliases- shortcuts to keys (per region)

### Permissions
Starting point for security is key policy (like bucket policy)
  - every key has one
  - must explicitly allow account, trust isn't automatic
  - Key policies trusting the account + IAM policies to interact with key
  - samle IAM policy- permissions to use key to encrypt and decrypt
Key Policies + Grants (later)

## Demo - KMS

## S3 Object Encryption CSE/SSE
Buckets aren't encrypted, objects are

Various encryption options available within S3
- Client or Server side
- Users/App -> S3 Endpoint -> S3 Storage
  - Data to and from S3 generally encrypted in transit
  - Client-side- encrypted by client before it leaves
  - Server-sde (SSE)- not encrypted before its sent
  
Client-Side Encryption- YOU control keys, process, tooling
SSE- S3 handles some or all of process
- encryption at rest now mandatory in S3

3 Types:
- SSE-C - Server-Side Encryption with Customer-Provided Keys
  - Customer:Keys, Amazon:CryptoOperations
  - S3 doesn't have key, to decrypt, give key to S3
  - good in regulation heavy environments
- SSE-S3 - Server-Side Encryption with Amazon S3-Managed Keys (DEFAULT)
  - AWS handles keys and crypto operations
  - key for every object
  - S3 creates, manages, and rotates (you have no control), all behind the scenes
  - uses AES-256
  - 3 problems: no control in regulated env., no rotation control, no role separation (full S3 admin can decrypt and view. might not be allowed in some industries)
- SSE-KMS - Server-Side Encryption with KMS Keys stored in AWS Key Management Service
  - use KMS service to manage keys
  - custom managed KMS key, isolated permissions, key is fully configurable
  - KMS deliver plaintext and ciphertext versions of key, object encrypted, discards plaintext key, object and cipher key stored in S3
  - KMS doesn't store data encryption keys, only creates and distributes them
  - good for regulated industries
  - role separation- to decrypt you need access to original KMS key
    - S3 admin can't decrypt data

2 components:
- encrypt/decrypt process
- generation and management of keys

## Demo - Object Encryption and Role Separation
S3 - Create bucket
KMS - Create symmetric key, no permissions defined (only trusts account)
S3 Bucket - Upload object, Properties... SSE... Specify an encryption key... Override bucket settings... SSE-S3... Upload
  - Upload object, Properties... SSE... Specify an encryption key... Override bucket settings... SSE-KMS... Choose from your AWS KMS keys... Default key... Upload
  - Upload object, Properties... SSE... Specify an encryption key... Override bucket settings... SSE-KMS... Choose from your AWS KMS keys... Custom(catpics) key... Upload
Apply deny policy to IAM user which restricts KMS... Can't open S3 objects with KMS encryption
Key rotation- can manage with SSE-KMS

## S3 Bucket Keys
S3- when you use KMS, each object uses a unique DEK
- PUT operation, S3 calls KMS to create DEK, object encrypted, object and key stored together
- every object get a uqique call to KMS
  - each DEK is an API call to KMS
  - Calls to KMS have a cost and levels where throttling occurs: 5,550 or 10,000 or 50,000 p/s

Time Limited *Bucket Key* used to generate DEKs within S3- offloads work from KMS to S3
- reduce cost, improve scalability
- CloudTrail KMS evens now show the bucket ARN, fewer events for KMS in logs
- Works with replication, object encryption is maintained
- replicating plaitext object- S3 encrypts object with destination bucket config (ETAG changes)

## S3 Object Storage Classes (20')
S3 Standard (DEFAULT)
- 3 AZs
- 99.999999999% durability (11 9s)
- Object stored: HTTP/1.2 200 OK statusprovided by S3 API Endpoint
- billed GB/month fee
  - $ per GB transfer OUT (IN is free)
  - $ per 1,000 requests
  - no specific retrievel fee, no min duration or size
- available within milliseconds, can be made publically available
- should be default choice, use for *frequently accessed data*

S3 Standard-IA (Infrequent Access)
- shares most characteristics with Standard
- storage cost cheaper (about 1/2)
- retrievel fee $ per GB in addition to transfer fee
- min duration of 30 days, min 128KB per object
- used for long-lived data that is important, but access infrequent
  
S3 One Zone-IA
- cheaper than Standard or IA
- similar to Standard
- data stored only in 1 AZ in region, no replication
  - additional risk of data loss
  - same level of durability, still replicated within AZ
- use for infrequently accessed data, data that can be easily replaced
- don't use for only copy/critical data/frequently accessed data

S3 Glacier-IA
- like Standard-IA, but cheaper, more expensive retrieval, longer minimum
- min duration 90 days
- less frequent access than Standard-IA
- can still use like S# standard, just costs more to access

S3 Glacier-Flexible
- Flexible Retrieval
- about 1/6 cost of standard
- think of objects as "cold"- not imediately available
- must perform retrieval process (job)
- retrieved objects temp stored in Standard-IA
- 3 types of retrievel jobs:
  - Expedited (1-5 minutes)
  - Standard (3-5 hours)
  - Bulk (5-12 hours)
- Faster = More Expensive
- 40KB min billable size, 90 day min billable duration
- when you need to store data where access isn't needed frequently
  
S3 Glacier Deep Archive 
- cheapest storage, but more restrictions
- think "frozen"
- 40KB min size, 180 min duration
- can't be made public, need retrieval job, temp restore to Standard-IA
  - Standard (12 hours)
  - Bulk (up to 48 hours)
- Not suited to primary system backups, use for archival backups or secondary backups

 Intelligent-Tiering
- 5 Tiers
  - Frequent Access
  - Infrequent Access
  - Archive Instant Access (90 day min)
  - Archive Access (optional, 90-270 days)
  - Deep Archive (like Glacier DA) (optional, 180 or 730 days)
- Moves between tiers for you
- Usage monitored, 30 days -> Infrequent tier
  - can add confi based on bucket or object tag
- Objects can be moved up to frequent automatically if accessed
- designed for long-lived data where usage is changing or unknown
  
## S3 Lifecycle Configuration
LifeCycle rules on S3 buckets
- automatically transition or expire objects
- automate costs

Set of rules applied to a bucket based on criteria
- whole bucket or groups of objects
- Transistion Actions - move between S3 tiers (maybe 30 days, then 90 days)
- Expiration Actions - can delete objects or versions

Rules based on access
Manage complete lifecycle
- Accessed over 30 days (Standard) -> less frequently for 90 (Standard-IA or Glacier) -> no longer required (Expiration)
- can go directly between mot classes
  - transition only down
- smaller objects have minimums, can end up with equal or more costs
  - look at minimum duration and size (e.g. object needs to be Standard for 30 days)
- Single rule to transition access- wait 30 days before transferring to Glacier, single rul can't transfer to IA, then glacier (2 rules)


## S3 Replication (14')


## Demo - Cross-region Replication of an S3 Statis Website (20')


## S3 PreSigned URLs (11')


## Demo - Creating and using PresignedURLs (18')

## S3 Select and Glacier Select (6')

## S3 Events (5')

## S3 Access Logs (3')

## S3 Object Lock (10')

## S3 Access Points (6')

## Demo - Multi-Region Acces Points (MRAP) (20')


