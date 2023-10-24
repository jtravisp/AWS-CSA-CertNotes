# Fundamentals

## AWS Global Infrastructure

### Regions
inside is full deployment of AWS infra.
N. Va, Oregon, London, etc.
geographically spread (withstand disasters)

- Geographic separation- isolated fault domain
- Geopolitical separation- diff governance
- Location control- tune performance

Region code or Region name
e.g. Asia Pacific (Sydney) or  ap-southeast-2
CLI/API uses region code

- Availability Zone (AZ)- multiple inside of each region (2-6)
	- isolated infra. inside each
	- outages should only affect one at a time
	- one availability zone could be multiple data centers (AWS doesn't tell you)
	- you can create a VPC across multiple AZs

### Edge Locations (local distribution points)
much smaller
Content Distribution Services
e.g. Netflix store content closer to customers

EC2- must select region
IAM, Route 53- global

--- 

- Define *resilience of service*
	- Globally resilient (few in AWS)- data replicated across multiple regions, e.g. IAM, Route 53
	- Region resilient (single region), replicate data to multiple AZs
	- AZ resilient (single availability zone)- most prone to failure

---

## Virtual Private Cloud (VPC) Basics

- create private networks inside AWS, connect VPC to on-prem or other cloud platforms

### VPC is within *1 account and 1 region*

### Private and Isolated unless you decide otherwise

### Two types - Default (1 per region) and Custom (many per region)
- Default created for you, less flexible than Custom

- VPC private by default (traffic can't cross boundry)
- VPC CIDR- defines start and end of IP addresses, everything inside uses CIDR range
	- *Default* is always 172.31.0.0/16, always configured same way
	- each subnet in a VPC is in one AZ
	- default has one subnet in every AZ in region
	- each subnet uses part of CIDR range, /20 in each AZ in the region
		- SN-A 172.31.0.0/20 - 172.31.15.255
		- SN-A 172.31.16.0/20 - 172.31.31.255
		- SN-A 172.31.32.0/20 - 172.31.47.255
	- some services assume default VPC exists, but probably don't use it for production
	- Default provided Internet Gateway (IGW), Security Group (SG), and NACL
	- Default subnets assign public IPv4 addresses

- Demo
	- VPC in console, Your VPCs
	- You will find default VPC
		- for us-east-1: 6 AZs, so 6 subnets
		- you can delete the VPC
	- Actions... Create default VPC... if needed

---

## EC2 Basics

Elastic COmpus Cloud
- IAAS
- VM = Instance
- Private by default- uses VPC
- Az resilient (fails if AZ fails)
- On-demand billing
- Local storage or Elastic Block Store (EBS)

States
	- Running
	- Stopped (storage still allocated adn charged $)
	- Terminated (fully deleted, including disk)

AMI- Amazon Machine Image
	- used to create instance, or instance used to create AMI
- Permissions
	- contain attached permissions, can be public
	- Owner- implicit allow use
	- Explicit- *specific AWS accounts allowed*
- Root Volume
- Block Device Mapping

Connecting
- Windows RDP port 3389
- Linux SSH port 22, priv/pub keypair

## EC2 Demo
jtravsp-io-general
A4L.cer private key file


## S3
- Global
- Regionally resilient (stored across all AZs in region)
- Public- accessible from aywhere

### Objects 
Key = filename
Value = data or contents, size, o to 5TB
Also... :
	Varsion ID
	Metadata
	Access Control
	Subresources

### Buckets
Created in an AWS region
name must be golbally unique
unlimited objects
flat structure
- aren't really folders, even though it looks that way
- "folders" are really prefixes
name 3-63 characters, all lwercase, no underscores
soft limit of 100, hard limit of 1000 (with support requests)

- Object store, not block storage
- Can;t mount S3 bucket
- Good for large scale data storage
- Good for offload
- I/O to MANY AWS services

 ## S3 Demo

## CloudFormation (CFN)
- template to update infrstructure 
- JSON or YAML
- "resources" section only mandatory

### YAML
```
AWSTemplateFormatVersion: "version date" # isn't mandatory

Description: # free field to describe template, imm. follow template format version
	String

Metadata: # can control how template presented in UI
	template metadata

Parameters: # prompt user for more info, e.g. size of instance, number of AZs to use
	set of parameters

Mappings: # create key/value pairs for lookups
 set of mappings

Conditions: # e.g. create resource if condition met
	set of conditions

Outputs: # e.g. return instance ID of created instance
	set of outputs
```

### Template
- resources are called "Logical resources"
Create EC2 instance:
```
Resources:
Instance:
	Type: 'AWS::EC2::Instance' # what to create
	Properties:
		ImageID: !Ref LatestAmiId
```
CF creates a "Stack" with all logical resources the template asks to create
Logical resource -> Physical resource
CF keeps logical and physical resources in sync
Update tamplate -> CF updates physical resources (create, delete, modify)

## CFN Demo

---

## CloudWatch (CW)
- Collects and manages operational data
	- Metrics- AWS products, on-prem e.g. cpu utilization (can install CloudWatch Agent)
- Metrics
- Logs
- Events (e.g. billing alarm)
need to install CW agent for non-native apps

- Namspace - contrainer for monitoring data
	- all goes into AWS/<service name>
	- e.g. AWS/EC2
	- namespaced contain related metric
metric- related data points, time-ordered
	not for a specific server
datapoint- eash measurement,
	- timestamp
	- value
dimensions
	- separate datapoints for different things, using key:value
	- e.g. cpu stilization includes AWS/EC2 includes instanceID and instanceType
alarms - OK, alarm, insufficient data states
	- linked to a metric
	- takes action based on criteria
	- alarm state -> action (notification or anything else)
	- e.g. billing alarm

## CW Demo
 ---

## Shared Responsibility Model
- part responsibility with vendor, part with you

### AWS- security OF the cloud
Hardward/AWS Global Infrastructure
Regions/AZs/Edge LOcations
Software
Compute/Storage/Database/Networking

### Customer- security IN the cloud
Client side data encryption
Server-side encryption
Networking traffic protection
OS, Network
Platform, applications, identity and access management
Customer Data

- helpful to understand in exam - keep this in mind when learning about AWS products

---

## High Availability (HA) vs Fault Tolerance (FT) vs Disaster Recovery (DR)

### HA
- ensure agreed level fofperformance, uptime higher than normal period (old definition), doesn't mean never fails
	- on failure, components replaced quickly
	- 99.9% - 8.77 hours per year down
	- 99.999% - 5.36 minutes per year down
	- HA- minimizing outages, users might have inconvenience like re logging in
	- fast recovery
	- maybe redundant servers/infra.

### FT
- more than HA
	- system continues operating properly in event of the failure of some of its components
	- continues operating in a failure without impact
	- when HA isn't enough, FT systems *operate through failure*
	- minimize outages, but also tolerate failure
	- airplane- more engines than it needs, duplicate systems, can operate through failure 
	- much harder to implement that HA

### DR
- policies, tools, and procedures to enable recovery or continuation of vital tech infra. and systems following natural or human-induced disaster
- Pre-planning -> Disaster -> DR Process
- Local infra.- need resilience (e.g. backup VMs in the cloud)
- Backups off-site, restored at standby location
- copes of processes available, logins
- Do DR testing
- think pilot/passenger ejection systems- don't lost anything that can be replaced, then recover

---

## Route 53

Manages DNS root zone- IANA

### Register Domains
	- .org registered with PIR
Create zone file for domain being resistered
Allocate nameservers for each zone (4 per zone), put zone file onto all 4 servers
Adds nameserver records to zone file for top level domain, delegates admin of daomain
	- indicates our 4 nameservers are authoritative

### Host Zones (managed nameservers)
Zone files in AWS
Hosted on 4 managed name servers
Can be public 
	- or private (linked to VPC(s))
	- sensitive DNS records

- Global (single database), globally resilient

## Route 53 Demo

### Hosted Zones 
databases that store your DNS records
4 nameservers allocated every time you create a hosted zone
will see name servers attached to domain names here

### Registered Domains
Register, transfer
small monthly cost for each hosted zone
Domains... Requests.... for domain reg. status
DNS system points at name servers, allocated automatically


## DNS Record Types

### Nameserver (NS)
delegation
.com zone will have mult. NS records inside
	- e.g. Root -> to .com zone -> to amazon.com zone

### A and AAAA
Host -> IP
A maps www to IPv4 address
AAAA maps to v6 address
Create 2 records with same name, one A, one AAAA

### CNAME
Host to Host, DNS Shortcuts
A server -> IPv4
Reduce admin overhead, e.g.
	- CNAME ftp -> A server
	- CNAME mail -> A server
	- CNAME www -> A server
auto updates when A record update

### MX record
email server needs to know where to pass email
google.com A mail zone -> IPv4
MX 10 mail (assumes mail.google.com)
MX 20 mail.other.domain. (FQDN, insdie same zone or outside, like Microsoft mail)

number is priority value, lower number = higher priority
Connects to mail IP with SMTP

### TXT record
arbitray text to provide additional functionality
Email system might ask for TXT record, query text data, proof of ownership

### TTL - Time to Live
numeric value in seconds
client -> resolver -> root -> .com -> amazon.com (www TTL 3600) (authoritative answer)
client -> amazon.com
TTL value- how long to cache value
3600 = 1 hour
resolver server can cache DNS resolution for 1 hour
High TTL value, change mail provider- might be a delay in change
Low values=more queries
High values=less, but less control over change
