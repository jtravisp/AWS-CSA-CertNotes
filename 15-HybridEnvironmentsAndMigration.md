# Hybrid Environments and Migration

## Border Gateway Protocol 101 (BONUS content)

Routing protocol,  used by some AWS services such as Direct Connect and Dynamic Site to Site VPNs.

- Autonomous System (AS)- routers controlled by one entity... a network in BGP
  - black boxes that abstract away detial
- ASN are unique and allocated by IANA, typically 16-bit (0-65535, 645122-65534 are private)
- BGP operates over tcp/179- it's reliable
- Not automatic- peering is manually configured
  - each system exchanges network topology info with each other
- BGP is a path-vector protocol, it exchanges the best path to a destination between peers, doesn't accout for link speed or condition, the path is called the ASPATH
- iBGP = Internal BGP- routing withing AS
- eBGP = External BGP- routing between ASs

### BGP Topology

Brisbane (ASN 200) 10.16.0.1/16 <-> Adelaide (ASN 201) 10.17.0.1/16 <-> Alice Springs (ASN 202) 10.18.0.1/16

- Brisbane routes table contains Destination, Next Hop (0.0.0.0. means local), ASPATH (i means this network)
- each peer will excahnge best path to a destination with each other, at first only itself
- Brisbane adds Destination 10.17.0.0/16, Next Hop 10.17.0.1, ASPATH 201,i
  - same for Alice Springs router destination, Brisbane now knows about both other ASs
  - Adelaide in the same way will learn about network in Alice Springs
  - Alice Springs will also learn about Brisbane and Adelaide ASs
  - networks can route traffic to other 2
- Brisbane adds another route for going other direction to Alice Springs 10.17.0.01/16
  - Destination 10.18.0.0/16, Next Hop 10.17.0.1, ASPATH 201,202,i
  - prepend own ASN onto path
- AS advertise shortest route to other systems
- end up with HA network, BGP aware of multiple routes in case one fails
  - longer paths are non-preferred, BGP prefers shortest path
- shortest connection might be slower (e.g. fiber vs satellite), but BGP would use by default
  - AS Path Prepending can be used to artificially make the satellite path look longer making the fiber path preferred
  - ASPATH 202,202,202,i
- BGP networks work together to create a dynamic topology

## IPSec VPN Fundamentals

- IPSec is a group of protocls- sets up secure tunnels across insecure networks
- ...between two peers (local and remote)
- Provides authentication... and encryption

Public Internet (insecure)- create tunnels between peers
- created as required **interesting traffic** or tunnels torn down until needed again
- Data inside tunnels is encrypted- secure connection over insecure network

- Reminder- symmetric encryption is fast... but challenging to exchange keys securely
- Asymmetric encryption is slow... but can easily exchange public keys

IPSec Phases- has two
- IKE (Internet Key Exchange) Phase 1 (slow and heavy)
  - 2 versions, 2 is newer with more fetures
  - Authenticate- pre-shared key (password)/certificate
  - using asymmetric encryption to agree on, and create a shared symmetric key
  - IKE SA (phase 1 tunnel)
- IKE Phase 2 (fast and agile)
  - uses the keys agreed in phase 1
  - agree encryption method, and keys used for bulk data transfer
  - Create IPSEC SA... phase 2 tunnel (architecturally running over phase 1)

### IKE Phase 1:

Routers authenticate- certificate of pre-shared key authentication
Diffe-Hellman (DH) Key exchange, each side creates a DH private key and derives a public key
Public keys are exchanged over the public internet
Each side takes own private key and public key from other side, independently generates the "same" shared Diffie-Hellman key
Using DH key, exchanges key material and agreements
Each side generates a symmetrical key- using DH key and exchanged material

### IKE Phase 2:

DH key on both sides, public key on both sides, established phase 1 tunnel
Symmetric key is used to encrypt and decrypt agreements and pass more key material
"Best shared" encryption and integrity methods communicated and agreed
DH key and Exchanged Key Material is used to create symmetrical IPSEC key
IPSEC key is used for bulk encryption and decryption of interesting traffic

Two types of VPNs:
- Policy-based VPN
  - rule sets match traffic -> a pair of SAs... different rules/security settings
  - same phase 1 tunne, each policy match using unique key
  - diff sec settings for diff types of traffic
  - more difficult to configure, more flexible
- Route-based VPN
  - target matching (prefix)... matches a single pair of SAs
  - Phase 1 tunnel key
  - single phase 2 tunnel running over phase 1 tunnel
  - dropped when no interesting traffic

## AWS Site-to-Site VPN

Create network link between AWS and something not AWS

- logical connection between a VPC and on-prem network encrypted using IPSec, running over the public internet
- Full HA- if you design and implement it correctly
- quick to provision... less than an hour
- Virtual Private Gateway (VGW)- gateway object, target on 1 or more route tables
- Customer Gateway (CGW)
- VPN Connection between the VGW and CGW

AWS Site-to-Site VPN
VPC (3 subnets in 3 AZs) (10.16.0.0/16) - AWS Public Zone (VGW) - Public Internet - Office (192.168.10.0/24)
Create Customer Gateway (CGW), ext IP 1.3.3.7 at Office
VGW in AWS Public Zone has physical Endpoints (HA if at least one endpoint functioning), each with public IPv4 addresses
Create VPN connection inside AWS (can be static or dynamic), create static for now, linked to Virtual Private Gateway
VPN tunnels created between each endpoint and to the Customer Gateway
  - tell AWS side what network range in use on-prem and vice versa, traffic can flow from VPC through gateway to on-prem and back again
  - single point of failure- Customer Gateway router (partial HA)
Fully HA- add another on-prem router (preferably in second building)
  - creates two more endpoints connected to same gateway on AWS side, new tunnels to second router
  - makes VGW HA, endpoints in diff AZs

Static v Dynamic (BGP) VPN
Both: VPC -> VPC Router -> VGW -> On-Prem CGW Customer router
- Static- static networking confg- static routes in route table
  - simple, just IPSec
  - restricted on LB, multi connectionfailover
- Dynamic uses BGP, routers exchange information
  - BGP configured on both customer and AWS side using ASN
  - multiple VPN connections provide HA and traffic distribution
  - Route propogation (if enabled) means routes are added to RTs automatically

VPN Considerations
- Speed limitations ~1.25 Gbps (AWS limit) (overhead on encryption/decryption)
- Latency Considerations- inconsistent, public internet (could be many hops between you and AWS endpoint)
- Cost- AWS hourly cost, GB out cost, data cap (on premises)
- Speed of setup- hours... all software defined configuration (but need BGP support for dynamic)
- Can be used as a backup for Direct Connect (DX)
- Can be used with Direct Connect (DX)

## Simple Site2Site VPN - DEMO (5 stages)

pfsense free trial: https://aws.amazon.com/marketplace/pp/prodview-gzywopzvznrr4
https://github.com/acantril/learn-cantrill-io-labs/tree/master/aws-simple-site2site-vpn
Need key pair in N Virginia region, name "infra", .pem, Create
Starting state (1-click deployment): AWS VPC with 2 subnets (2AZs), On prem router and private server (use created key pair)

### Stage 1 - Create Site2Site VPN 
Get external IP of customer router (onprem pfsense) from stack
VPC... Create VPN customer gateway... skip bgp and cert... Create
VPC... Create VPN VPG... Create, attach to VPC
VPC.... VPN site-to-site VPN connection, Visrtual private gateway (AWS side endpoint type)... select private gateway created above, customer gateway: on-prem router, routing options: static, IP prefixes- use range n on-prem env (BGP would do this automatically)... Create
Will be in Pending state for a bit... download configuration (needed to configure pfsense), choose vendor pfsense and version number

### Stage 2 - Configure onpremises Router
Ec2... Instances running... Select onprem router... monitor and troubleshoot...get system log to get username and password
  - open IPv4 address to connect to router, sign in with pw copied above, don't follow wizard
  - Interfaces... assignments.... add detected LAN interface
  - Interfaces, enable LAN interface, choose DHCP (for production, choose static), save and apply
Phase 1 and Phase 2 config for each endpoint (total of 4 configs)
Use config from downloaded file, keep file open, config for tunnel 1 and 2
IPSec Tunnel $1
  - Phase 1 configuration: Click +Add P1, Key Exchange ver IKEv1, IPv4, Interface: WAN, Remote Gateway <IP of endpoint 1 on AWS side>
  - Auth Method: Mutual PSK, Negotiation: Main, PSK from config generated by AWS
  - Encryption: AES 128, SHA1 hasg, DH Group 2(1024bit), Lifetime 28800, Dead peer detecton yes, NAT traversal auto, delay 10, maxFailures 3, Save
  - Phase 2 configuration: Show sphase 2 entries, +Add P2
  - Local network: networkk, 192.168.10.0/224 (private network in on-prem environment)
  - Remote network 10.16.0.0/16 (AWS network) 
  - Follow same process for endpoint 2
Now created Phase 1 and 2 config for both tunnels (both endpoints at AWS side)
Apply changes in pfsense, manually connect both tunnels

### Stage 3 - Routing & Security
Configure routing and security groups in both environments
AWS Side- Route tables, 3 route tables creaded by deployment
  - rt-aws attached to both subnets, can create static route or use route propagation
  - Click route propagation, enable, should pick up IP range used in on-prem env automatically
  - AWS side infra now knows how to route to on-prem
On-Prem Side
  - simulated with rt-onprem-private
  - edit routes, any traffic destined for AWS, point at pfsense firewall, enter AWS IP range (10.16.0.0/16)
  - Target: network interface within private subnet, Save
  - Both sides now know how to reach the other, but security groups in the way
On-prem firewall simulated with AWS security groups
Security Groups- AWS Side
  - Add new rule for on-prem network
  - All traffic, enter network range used by on-prem env (192.168.8.0/21), description: allow on-prem in
Security Group- On-prem Side
  - Add rule, all traffic, IP range for AWS VPC (10.16.0.0/16)
Security Group- On-prem router
  - acting as VPN endpoint, need to allow anything running on-prem to access
  - allow IP range, add rule, all traffic, find on-prem security group

### Stage 4-5 - Testing & Cleanup
Go to EC2 instances running
  - Simulated onpermRouter, onpremServer, and awsServerA
  - Open onpremServer, RDP client, connect using Fleet Manager (for graphical UI), click "get password", open FM remote desktop
  - enter user/password, connect, try pinging aws server, goes over site to site VPN to confirm it's working

Cleanup
  - Manually delete VPN config in VPC console
  - detach gateway from VPC, delete gateway, delete customer gateway, delete CF stack
  
## Direct Connect (DX) Concepts
AWS Direct Connect links your internal network to an AWS Direct Connect location over a standard Ethernet fiber-optic cable. 
One end of the cable is connected to your router, the other to an AWS Direct Connect router. 
With this connection, you can create virtual interfaces directly to public AWS services (for example, to Amazon S3) or to Amazon VPC, bypassing internet service providers in your network path. 
An AWS Direct Connect location provides access to AWS in the Region with which it is associated. You can use a single connection in a public Region or AWS GovCloud (US) to access public AWS services in all other public Regions.

- Physical connection (1, 10, or 100 Gbps)
- Business prem -> DX Location -> AWS Region
- actually ordering a port allocation at DX location
- Port hourly cost and outbound data transfer
- One allocated, you arrange connection at DX location, plan on weeks or months of time for Business prem -> DX location
- Physical cables
- Low and consistent latency + High speeds, best way to achieve highest speeds with AWS
- dedicated port means you can achieve highest possible speed
- AWS Private services (VPC) and AWS Public services - No Internet

Architecture
- Business premises -> DX Location (not owned by AWS, often regioanl large data center with space rented by AWS): AWS Direct Connect cage with endpoints + Customer or Comms Partner cage with Customer/Partner DX router
  - DX port connected to your router or Comme Partner router - Cross Connect, physical cable connecting AWS port to yours/partners
  - -> AWS Region with VPC and public zone services

## Direct Connect (DX) Resilience and HA
Understanding of failures in DX architecture
Not resilient (and how most people provision DX):
- AWS Region  -> DX Location -> Customer Premises
  - AWS region connected to all DX locations via redundant high speed connections
  - inside DX locaiton- collection of AWS DX routers, hen ordering DX connection, you get one port on a router, connect to customer or provider DX router, you arrange the connection (Cross Conncet), then connect DX location to company network
  - probably pay telecom provider to extend DX connect to on-prem network
  - What can go wrong? 7 points of failure!
    - entire DX location could fail
    - AWS DX router could fail
    - Cross connect cable could fail
    - your DX router could fail
    - extension to on-prem location could fail (long cable run)
    - failure of on-prem env
    - or on-prem router
  - DX is not resilient by default, lots of physical components that depend on each other

How to improve resilience?
- Multiple DX ports, multiple cross connects into multuiple customer routers, multiple connections to on-prem
  - architecture can tolerate a failure of one port/router/connection
  - if DX location itself fails, connectivity still lost
  - physical cable route to on-prem could be the same (single point of failure)
  - totally separate business permises increases resilience
- Extreme resilience:
  - Aws region -> 2 DX locations (with 2 DX ports each) -> 2 Business premises

## Direct Connect (DX) - Public VIF + VPN (Encryption)
Neither public or private VIFS offer any form of encryption.
Public VIFs+IPSec VPN is a way to provide access to private VPC resources, using an encrypted IPSEC tunnel for transit.

Public VIF + VPN - authenticated and encrypted tunnel
- Over DX (low latency and consistent latency)
- Uses a public VIF + VGW/TGW public endpoints
  - private VIF gives access to private IPS only, public VIF gives access to public IPs belonging to VGW/TGW
  - what is it you're trying to access? 
- VPN is transit agnostic (DX/Public internet)
- End-to-end CGW<->TGW/VGW - MACsec is single hop based
- VPNs- wide vendor support
- VPN has more cryptographic overhead compared to MACsec... limits speeds
- VPN can be used  while DX is provisioned and/or as a DX backup
  - DX primary, backup is VPN

VPNs in AWS public zone with public addressing, many hops, variable latency
Public VIF transit- direct and low latency
VPN is for when you need end to end encryption, can connect to remote regions with same equipment

Public IP? use public VIF

## Transit Gateway (TGW)

The AWS Transit gateway is a network gateway which can be used to significantly simplify networking between VPC's, VPN and Direct Connect.
It can be used to peer VPCs in the same account, different account, same or different region and supports transitive routing between networks.

- Network Tansit Hub that connect VPCs to each other and on-prem networks
- reduces complexity of network architecture in AWS
- Sing network object- HA and scalable
- Attachments to other network types
- VPC, site-to-site VPN, and Direct Connect Gateway

Architecture
- 4 VPCs, VPC peering connections can be used, but don't support transitive routing, would need 6 connections
- 8 connections total from AWS to 1 customer router, HA on AWS side, but not on-prem side, must add 2nd gateway, preferably diff site
  - 8 additional connections, gets complicated, lots of admin overhead
  - Scales badly
- Using Transit Gateway
  - Same 4 VPCs
  - Create Transit Gateway in AWS account, becomes AWS side termination point for VPN
  - each customer gateway only connects to that gateway (not every VPC), still HA
  - VPC attachments are configured with a subnet in each AZ where service is required
    - all VPC can talk to each other through TGW
    - also on-prem <-> VPCs communication
    - Peering across cross-region, same/cross-account
  - Can connect TGW to DX gateway
  - come with default route table
    - can use multiple route tables

- Does support transitive routing, will orchestrate routing
- Can be used to create global networks
- Can share between different AWS accounts
- Peer with different regions... same or across accounts
- Less complexity vs w/o TGW 

## Storage Gateway - Volume

Storage gateway is a product which integrates local infrastructure and AWS storage such as S3, EBS Snapshots and Glacier.
This lesson looks at Gateway Volume - Stored and Gateway Volume Caches

Runs as a VM on prem (or hardware applicance)
- bridge between local and cloud storage, using iSCSI, NFS, or SMB (Windows)
- integrates with EBS, S3, and Glacier within AWS
- Migrations, Extensions, Storage Tiering, DR, and Replacement of backup systems (tape)
- For exam: pick the right mode

Storage Gateway
- NAS or SAN on prem, Sservers with local disks
  - generally use iSCSI, Block devices
- Stored Mode
  - virtual applicance presents volumes over iSCSI to on-prem servers, look just like NAS or SAN
  - create file systems on top of volumes, just like NAS/SAN
  - consume capacity on-prem
  - Upload buffer- data written to local storage written here, then copied to Storage Gateway Local Storage
  - Gateway VM -> AWS SG Endpoint -> EBS Snapshots
  - great for full disk backup of servers, can be quickly restored
  - great for Disaster Recovery, create EBS volumes in AWS
  - does not allow extending capacity, primary location is on-prem
  - 32 volumes per gateway, 16TB per volume, 512TB per gateway
- Cached Mode
  - still SG VM -> SG Endpoint
  - main location for data is no longer on-prem, next step is -> Primary Storage S3 (AWS managed, only visible from SG console, raw block storage) -> optional EBS snapshots
  - primary data is in S3, only frequently accessed data is on-prem
  - Datacenter Extension architecture, AWS is an extension of on-prem
  - storage appears on-prem
  - 32TB per volume, 1PB per gateway, 32 volumes per gateway

## Storage Gateway - Tape (VTL)
Storage gateway in VTL mode allows the product to replace a tape based backup solution with one which uses S3 and Glacier rather than physical tape media.
VTL = Virtual Tape Library

- Large backups -> Tape
  - LTO - Linear Tape Open, LTO-9 Media can hold 24TB Raw Data
  - ...up to 60TB compressed
  - 1 tape drive can use 1 tape at a time
  - not easily updated, designed as write or read as a whole
  - Loaders (robots) can swap tapes
  - A Library is 1+ drive(s), 1+ loader(s) and slots
  - Drive... Library... Shelf (anywhere but the library) - throwback to physical world
- Traditional Tape Backup
  - Business Premises
    - Backup Server -> iSCSI -> Media Change/Tape Drive(s)
    - Costs: Equipment (tapes, software, library)- CAPEX and OPEX costs
    - Offsite tape storage (often 3rd party) for resilience
    - Only tapes in physical library can be used, transport offsite take time and money
- Storage Gateway Tape (VTL)
  - SGW in tape mode instead of on-prem library, looks the same to backup server using iSCSI (server can't tell the difference)
  - SGW presents Media Changer and Tape Drive(s)
  - Upload Buffer and Local Cache (virtual tapes) -> AWS S3 (VTL) and Glacier Tape Shelf (VTS)
  - Virtual tape 100GB - 5TB
  - 1PB across 1500 virtual tapes max
  - exported tape - not in library, acrchives from VTL to VTS (library to shelf/Glacier)
  - can be retrieved from VTS (shelf) if needed
- Use existing backup, but replace expensive parts with AWS
- Can migrate historical set of tape backups to AWS and decommision local hardware

## Storage Gateway - File
File gateway bridges local file storage over NFS and SMB with S3 Storage

It supports multi site, maintains storage structure, integrates with other AWS products and supports S3 object lifecycle Management

- Volumes? default to Volume Gateway
- Tapes? default to VTL mode
- Files? default to file mode

- SGW File bridges on-prem file storage and S3- local files -> S3
- Mount Points (shares) available via NFS (Linux) or SMB (Windows)
- Map directly onto an S3 bucket, you have management and visibility of bucket
- Read and Write Caching ensures LAN-like performance

Architecture
- Business Premises
  - File Gateway Virtual Appliance, local storage
    - File Shares, each linked to single S3 bucket, Share -> Bucket = Bucket Share
    - Files visible both locations, structure preserved (S3 flat structure emulates folder structure by building it into name)
    - up to 10 shares per storage gateway
    - Can use S3 events and Lambda or anything else that works with S3
- Can implement multi-site
  - Add another on-prem environment, FileShare maps to same S3 bucket as other premises
  - Srv1 -> S3 -> Srv2
  - can create Cloudwatch event that informs other prem that file is new/changed
  - File Gateway doesn't support Object Locking- use read only mode on other shares or tightly control access
- Reaplication- can conif replication to another region
- Can use S3 lifecycle management
  - S3 Standard - Standard IA -> Glacier
  - config to move after period of time

## Snowball/Edge/Snowmobile
Snowball, Snowball Edge and Snowmobile are three parts of the same product family designed to allow the physical transfer of data between business locations and AWS.

- Move large amounts of data IN and OUT of AWS
- Physical storage- suitcase or truck
- Ordered from AWS with data OR empty & return
- For the exam, know which to use

Snowball
- ordered from AWS, Log a job, Device delivered 
- Data encrypted using KMS
- 50TB or 80TB
- 1Gbps (RJ45 1GBase-TX) or 10Gbps (LR/SR) Network
- 10TB to 10PB economical range (multiple devices)
- Multiple devices to multiple premises
- Only storage (no compute)

Snowball Edge
- Storage and Compute
- Larger Capacity vs Snowball
- 10 Gbps (RJ5), 10/25 (SFP), 45/50/100 Gbps (QSFP+)
- Storage Optimized (with EC2) - 80TB, 24 vCPU, 32 Gib RAM, 1TB SSD
- Compute Optimized - 100TB + 7.68 NVME, 52 vCPU and 208 GiB RAM
- Compute with GPU - as above, with a GPU
- Any remote sites with needs for data processing on ingestion, use Edge

Snowmobile
- Portable Datacenter within a shipping container on a truck
- Special order
- Single location with huge amounts of data, 10 PB+ is required
- Up to 100PB per snowmobile
- Not economical for multi-site (unless huge) or sub 10PB

## Directory Service
The Directory service is a product which provides managed directory service instances within AWS. It functions in three modes:

Directory- stores objects (e.g. Users, Groups, Computers, Servers, Files Shares) with a structure (domain/tree)
- multiple trees can be grouped into a forest
- common in Windows environments
- sign in to multiple devices with the same username/password, provides centralized management for assets
- e.g. MS Active Directory Domain Services (AD DS)
- AD DS most popular, open source alternatives SAMBA

AWS Directory Service
- AWS managed implementation
- Runs withing a VPC (private services)
- To implement HA- deploy into multiple AZs
- Windows EC2 instances can join directory
- Some AWS services NEED a directory, e.g. Amazon Workspaces (like Citrix)
  - requires registered directory inside AWS
- Can be isolate (inside AWS only)
- ...or integrated with existing on-prem system
- ...or act as a 'proxy' back to on-prem

Simple AD - An implementation of Samba 4 (compatibility with basics AD functions)
- cheapest and simplest
- Amazon Workspaces uses directory services
- Standalone directory which uses Samba 4
- Virtual desktop users -> Workspaces -> Simple AD
- up to 500 users (small) or 5,000 users (large)
- Designed to be used in isolation (not with on-prem systems)

AWS Managed Microsoft AD - An actual Microsoft AD DS Implementation
- Designed to have a direct presence in AWS, but with on-prem env
- can create trust relationship with on-prem directory (using direct connect or VPN)
- Primary running location is in AWS... Resilient if VPN fails... services in AWS will still be able to access the local directory inning in Directory Service
- Fulle MS AD DS running in 2012 R2 mode

AD Connector which proxies requests back to an on-premises directory.
- only want to use 1 specific AWS service that requires directory, don't want to create brand new directory
- AD Connector- private connectivty to on-prem, like VPN
- point AD connector back to on-prem directory
- just a proxy to integrate with AWS services, doesn't provide auth on its own, proxies requests back to on-prem env
- if private connectivity fails, the AD proxy won't function, interrupting AWS service

Picking....
- Simple AD is default, simple, just a directory in AWS
- MS AD- applications in AWS which need MS AD DS, or you need to Trust AD DS
- AD Connector- use AWS services that need a directory without storing any directory in the cloud... proxy to on-prem env

## DataSync
AWS DataSync is a product which can orchestrate the movement of large scale data (amounts or files) from on-premises NAS/SAN into AWS or vice-versa
- Data Transfer services TO and FROM AWS
- Migrations, Data Processing Transfers, Archival/Cost Effective Storage or DR/BC
- Designed to work at huge scale
- Keeps metadata (e.g. permissions/timestamps)- important for migrations
- Built in data validation (make sure data matches original)

Key Features
- Scalable - 10Gbps per agent (~100TB per day)
- Bandwidth Limits (avoid link saturation)
- Incremental and scheduled transfer options
- Compression and encryption
- Automatic recovery from transit errors
- AWS Service integration - S3, EFS, FSx
- Pay are you use- per GB cost for data moves

Corp on-prem env SAN/NAS Storage -> Data Sync Agent runs on vrtuzlization platform (VMWare)-> AWS DataSync Endpoint
- Schedules can be set to ensure the transfer of data occurs during or avoiding specific time periods
- Encryption in transit (TLS)
- Customer impact can be minimized by setting bandwidth limit in MiB/s
- next goes to S3, EFS, FSx for Windows Server, etc.

Components
- Task- a "job" within DataSync, defines what is being synced, how quickly, FROM where and TO where
- Agent- Software used to read or write to on-perm data stores using NFS or SMB
- Location- every task has two locations FROM and TO, e.g. NFS, SMB, Amazon EFS, Amazon FSx, and Amazon S3

## FSx for Windows Servers
FSx for Windows Servers provides a native windows file system as a service which can be used within AWS, or from on-premises environments via VPN or Direct Connect

FSx is an advanced shared file system accessible over SMB, and integrates with Active Directory (either managed, or self-hosted).

- different from EFS
- Fully managed native Windows file servers/shares
- Designed for integration with Windows environments
- Integrates with Directory Service or Self-Managed AD
- Single or Multi-AZ within a VPC
- On-demand and Scheduled Backups
- Accessible using VPC, Peering, VPN, Direct Connect (large enterprise with dedicated link)
- look for Windows related keywords, FSx vs EFS, EFS for Linux

Implementation
- VPC -> DC/VPN -> Corp network
- 2 AZs, 2 subnets in each
- DS inside subnet- supports managed or self-managed AD (on-prem), can integrate with normal implementation of AD that enterprise already has
- DS <-> FSx network share (\\fs-xxx123.animals4life.org\catpics - catpics is actual share)
- FSx <-> Workspaces (other subnet)
- Native Windows file system, supports de-duplication (sub file), Distributed File System (DFS), KMS at-rest encryption and enfroced encryption in transit
- Support volume shadow copies (file level vesioning)
- High performance, 8MB/s 2GB/s, 100ks IOPS

Features and Benefits
- VSS - User-driven restores (unique to FSx, view and restore previous versions)
- Native file system accessible over *SMB*
- Windows permission model
- Supports DFS... scale-out file share structure
- Managed- no file server admin
- Integrates with Directory Service AND your own directory

## FSx for Lustre
FSx for Lustre is a managed file system which uses the FSx product designed for high performance computing

It delivers extreme performance for scenarios such as Big Data, Machine Learning and Financial Modeling

- relatively niche
- managed implementation of Lustre file system- designed for HPC - Linux clients (POSIX)
- Machine learning, big data, financial modeling
- 100s GB/s throughput and sub millisecond latency
- Deployment types - Persistent or Scratch
- Scratch - highly optimized for Short Term, no replication and fast
- Persistent - longer term, HS (in one AZ), self healing
- Accessible over VPN or Direct Connect

- Managed file system accesible within VPC, connectivity-wise likfe EFS
- File Sytem- where data lives while proessing occurs
- Data is "lazy loaded" from S3 (S3 linked repository) into the file system as it's needed (not present until first accesed)
- no built-in sync
- Data can be exported back to S3 at any point using hsm_archive (NOT automatically in sync)

- Metadata stored on Metadata Targets (MST)
- Objects are stored on called object storage targets (OSTs) (1.17TiB)
- Baseline performance based on size
- For Scratch- base 200 MB/s per TiB of storage
- Persistent offers 50MB/s, 100MB/s, and 200MB/s per TiB storage
- Burst up to 1300MB/s per TiB (Credit System)

 Architecture
 - Client managed VPC (you design)
   - Clients (Linux EC2 with Lustre installed)
 - Lustre File System + optional S3 repository
   - product deploys storage servers to handle requests
   - delivered to VPC with single elastic interface
 - VPC ENI -> Lustre Disk
 - Storage volume -> ENI

- Scratch is designed for pure performance
  - short term or temp workloads
  - No HA, No replication
  - Larger file systems means more servers, more disks, more chance of failure
- Persistent has replication within ONE AZ only
  - auto-heals when hardware failure occurs
- You can backup to S3 with both! (Manual or Automatic 0-35 day retention)

- Windows/SMB? FSx for Windows, not Lustre
- Lustre, high end perf, POSIC, big data, machine learning? FSx for Lustre

## AWS Transfer Family
AWS Transfer Family is a secure transfer service that enables you to transfer files into and out of AWS storage services.

AWS Transfer Family supports transferring data from or to the following AWS storage services.
  - Amazon Simple Storage Service (Amazon S3) storage.
  - Amazon Elastic File System (Amazon EFS) Network File System (NFS) file systems.

AWS Transfer Family supports transferring data over the following protocols:
  - Secure Shell (SSH) File Transfer Protocol (SFTP) - FTP over SSH
  - File Transfer Protocol Secure (FTPS) - file transfer with TLS encryption
  - File Transfer Protocol (FTP)
  - Applicability Statement 2 (AS2)- niche, but common in certain sectors


- Managed file transfer service- supports transferring TO or FROM S3 and EFS
- Identities- Service manages, Directory Service, Custom (Lambda/APIGW)
- Managed File Transfer Workflow (MFTW)- serverless file workflow engine

Arhcitecture
- AWS Env- S3 and EFS
- AWS TRansfer Family server conifg for 1+ protocols
- User -> DNS -> Transfer Family -> IAM role -> S3/EFS
- Servers are front-end access points to storage (using protocols above)
  - Public- nothing to configure
    - only supported protocol is SFTP, Dynamic IP, can't control access via IP lists
  - VPC 
    - SFTP and FTPS
  - VPC - Internal
    - SFTP, FTPS, and FTP + AS2
  - both VPC types
    - SG and NACL can be used to control access
    - access from DX/VPN
- Multi-AZ- resilient and scalable
- Provisioned server per hour $ + data transferred $
- FTP and FTPS - directory service or custom IDP only
- FTP - CPV only (cannot be public)
- AS2 VPC Internet/internal Only
- If you need access to S3/EFS, but with existing protocols...
  - ...integrating with existing workflows
  - ...or using MFTW to create new ones
