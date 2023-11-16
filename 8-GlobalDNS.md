# Global DNS

## R53 Public Hosted Zones
A public hosted zone is a container that holds information about how you want to route traffic on the internet for a specific domain which is accessible from the public internet

- R53 Hosted Zone is a DNS DB for a domain (e.g. animals4life.org)
- Globally resilient (multiple DNS servers)
- Created with domain registration, can be created separately
- Host DNS records (e.g. A, AAAA, MX, NS, TXT, ...)
- Hosted zones are what the DNS system referecnes - Authoritative for a domain

R53 Public Hosted Zones
- DNS Database (zone file) hosted by R53 (Public Name Servers)
- Acessible from the public internet and VPCs
- Hosted on "4" R53 Name Servers (NS) specific for the zone
- ... use "NS records" to point at these NS (connect to global DNS)
- Resource Records (RR) created withing the Hosted Zone
- Externally registreed domains can point at R53 Public Zone

Public Hosted Zone -> 4 R53 NS Per Hosted Zone (available from public internet)(available from VPC)
    -  Inside: Resource Records
       -  www
       -  MX
       -  TXT
   - Within VPC: VPC +2 Address (R53 Resolver)- available from any EC2 instance
   - Public
     - Root servers (PC -> come ISP resolver -> Root Server -> .org NS records on .org TLD servers -> NS records on Public R53 Hosted Zone)

## R53 Private Hosted Zones
Like public in operation, but not public
- Associated with VPCs in AWS
- only accessible in those VPCs
- using diff accounts supported via CLI/API
- Split-view (overlapping public and private) for Public and Internal use with the same zone name

Private Hosted Zone
    - Inside: Resource Records
    - Inaccessible from public internet
    - VPC1, VPC2, VPC3- any VPC associated with Private Hosted Zone cas access, any not associated can't access

R53 Split View 
- Create Public Zone with same name
  - records in public zone accessible, but not private records

## CNAME vs R53 Alias
A rrecord maps a Name to an IP Address
  - catagram.io -> 1.3.3.7
CNAME maps a Name to another Name
  - www.catagram.io -> catagram.io
Can't use CNAME for naked/apex (catagram.io)
Mans AWS services use a DNS Name (ELBs)
With just CNAME- catagram.io -> ELB would be invalid

Alias Record- maps a Name to an AWS resource
 - Can be used for both naked/apex and normal records
 - For non apex/naked - functions like CNAME
No charge for alias requests pointing at AWS resources
For AWS services - default to picking Alias
Should be the same "Type" as what the record is pointing at
 - ELB - name -> IP, creat A record alias
 - Use Alias when pointing at API Gateway, CF, Elastic Beanstalk, ELB, Global Accelerator, and S3
Alias is outside usual DNS standard (R53 only)

## R53 Simple Routing
Hosted Zone (Public)
- 1 record per name
- A record - www
  - Each record can have multiple values
  - returned in random order, client chooses and uses 1 value
- Simple routing doesn't support health checks - all values are returned for a record when queried

## R53 Health Checks
Monitor the health and performance of your web applications, web servers, and other resources. Each health check that you create can monitor one of the following:
  The health of a specified resource, such as a web server
  The status of other health checks
  The status of an Amazon CloudWatch alarm

- Separate from, but are used by Records
- Health checkers locate globally (can check anything with an IP address)
- Check every 30s (every 10s costs extra)
- TCP, HTTP/HTTPS, HTTP/HTTPS with string matching (status code in 200 or 300 range, response body from endpoint, search for string you specify)
- Healthy or Unhealthy states
- 3 types: Endpoint, Cloudwatch Alarm, Checks of Checks (Calculated)

Route53 Console... Health checks... Create... Endpoint... IP or Domain Name... TCP, HTTP, HTTPS...
- Can send AWS SNS notifications or notify external service

## Failover Routing
Lets you route traffic to a resource when the resource is healthy or to a different resource when the first resource is unhealthy
- Add multiple records with same name, primary and secondary
- Primary and backup service
- Health check- primary record healthy, go to EC2 instance, Not healthy, queries return second record and go to S3 bucket

## Using R53 and Failover Routing - DEMO
Create CF stack... Public EC2 instance A4L-WEB
EC2 - Allocate elastic IP address, associate with EC2 instance
Create S3 Bucket (will be failover service), name bucket same as domain name (e.g. www.animals4life1337.org)
  - Host static website, upload web site files, bucket policy allowing public read
R53 Console... Health Check... A4L Health... Endpoint by IP, HTTP
  - Standard is 30s, 10s might be better for critical website
  - starts with Unknown status, then shows healthy or unhealthy
Hosted Zone... Create record... Failover record... Use elastic IP address... Record type Primary, select Health check ID
  - Another failover record for S3 bucket, Record type Secondary (only used if primary fails health check)
  - Simulate failure by stopping EC2 instance
  - Health check changes to Unhealthy
  - TTL was set to 60s, so after that time domain should change to failover secondary IP  

Create private hosted zone, associate with default VPC
  - Create record, simple 
  - A record point your made-up domain to test IP address
  - From web EC2 instance, ping record just created - "name or service not found" (because instance is in different VPC)
  - Change record, add A4L VPC, ping will still not work at first, after a few minutes will work

## R53 Multi Value Routing
Lets you configure Amazon Route 53 to return multiple values, such as IP addresses for your web servers, in response to DNS queries. 
You can specify multiple values for almost any record, but multivalue answer routing also lets you check the health of each resource, so Route 53 returns only values for healthy resources.
Mixture between simple and failover
- Start with hosted zone, many records with same name, each withnassociated health check
  - up to 8 records returned (selected at random), unhealthy records not returned
  - improves availability
  - not a substitute for load balancer, but uses DNS to improve availability
- Used when you have many resources that could be returned

## Weighted Routing
Lets you associate multiple resources with a single domain name (catagram.io) and choose how much traffic is routed to each resource. 
This can be useful for a variety of purposes, including load balancing and testing new versions of software.
- Starts with hosted zone, 3 www A records (maybe 3 EC2 instances)
  - each record has a weight, weight/total_weight = percentage of time that record returned
  - Group f records with same name and want to control distribution

## Latency-Based Routing
Used to optimize for performance and user experience
Starts with hosted zone and multiple records with same name
- Specify region for each record
  - IP lookup service used to find lowest latency, selects and returns that record
  - Can be combined with health checks
  
## Geolocation Routing
Similar to latency routing, but location used instaead of latency
Tag records with location- state, country, continent
IP check verifies location of user
- Doesn't return closest record, but only relevant (location) records - checks state first, then country, continent
- can also set default record if no match
- Useful for restricting content based on user location, providing regional content, or load distribution
- Again, NOT about CLOSEST

## Geoproximity Routing
Provides records that are as close as possible
- Similar to latency
- Define rules that routes you to resources in different regions
- Tag resrouces with AWS region or lat and long coordinates
- Can define + or - bias, e.g. effective area of resource is larger/smaller, maybe force Saudia Arabia customers to Australia by increasing Bias of Australia

## Interoperability
How Route53 provides Registrar and DNS Hosting features
Architectures where it is used for BOTH, or only one of those functions - and how it integrates with other registrars or DNS hosting.
Register a domain- R53 acts as registrar and provides domain hosting (can do one or both)
- R53 accepts domain registration fee, allocates 4 R53 DNS nameservers, creates zone file (domain hosting) on nameservers
- Communicates with the registry of the TLD (Domain Registrar)
- ...sets the NS records for the domain to point at the 4 NS above

Traditional- register and host with R53- Registrar liaises with R53 Domain Hosting - create public hosted zone
  - passes on to TLD (.org, .com, etc), entry added, using NS delegation records pointing to 4 NS

R53 Registrar Only, diff entity hosts domain, pass NS details of host to R53, Registrar adds TLD entry
- probably worst way to manage domain

R53 Hosting Only (more common)
- Domain registered with 3rd party, they lias with TLD registry
- Hosted zone with R53
- Can do this when regsitering domain and providing R53 NS, or add later

## Implementing DNSSEC with R53
Enabling DNSSEC on R53 hosted zone is done from console or CLI, done with KMS
- asymmetric key pair created- Public Key, Private Key
- need to be in US-East-1
- R53 creates zone signing keys nternally inside R53 (KMS not involved)
- R53 adds key signing key and zone signing key public parts into DNS key record in public zone
  - tells resolvers which public keys to use to verify records
- Private key signing key used to sign DNS key records- RRSIG DNSKEY
- Next, R53 established chain of trust with aprent zone
  - lias with appropriate TLD
- Configure CW alarms for DNSSECInternalFailure and DNSSECSigningKeyNeedingAction
- Consdier enablig DNSSEC validation for VPCs, if any records fail vailidation, won't be returned

### DEMO
Open R53... Hosted Zones... Open zone for your domain
- `dig animals4life.org dnskey +dnssec` - query for records with DNSSEC
- Go to DNSSEC signing, Enable (order matters here, consider TTL values)
- Create Key-signing key (using KMS key)
  - Pick name, Create customer managed CMK/KMS, Create name for key, Create and enable signing
  - Key signing key now active
  - dig command now returns DNSKEY records (public zone signing key)
- Create chain of trust with parent zone
  - Go to Registered domains (if domain registered with R53)
  - Changes here will lias with TLD zone
  - DNSSEC status- Click manage keys, enter public key signing key- KSK, View info from hosted zone, Establish chain of trust, check signing algo and match TLD setting, copy Public Key and paste in TLD settings
  - Also adds DS (delegated signer) record, hash of public key
  - Can take a few minutes to hours
  - DNSSEC status will change
- `dig org NS +short` - pick one
  - `dig animals4life.org DS @a0.org.afilias-nst.info`
  - no record? due to caching, wait... eventually will update with TLD
  - record contains hash of public key signing key, chain of trust established
  - new records will also be signed


