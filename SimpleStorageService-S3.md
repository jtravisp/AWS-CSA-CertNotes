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

# Demo - KMS
