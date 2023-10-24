# Elastic Compute Cloud (EC2)

## Virtualization 101
EC2 - IAAS

OS runs on top of hardware, Kernel operates in Priveleged Mode
Applications run in User, or Unpriveleged, Mode - Makes system call to Kernel

With virtualization - separate OSs, all expect to be priveleged
- Originally virtualization done in software
  - Host OS/Hypervisor
  - Each VM provided virtual hardware by hypervisor, guests "believed" they were "real"
  - Binary Translation: Hypervisor <-> VM OS (very slow)
- Para-Virtualization
  - Hypercalls instead of priveleged calls (OS modified to call Hypervisor, must be modified for particular vendor)
  - Massively improved performance, but still "tricks" OS and hardware
- Hardware Assisted Virtualization
  - Hardware becomes virtualization aware
  - CPU expects guest OS, Hypervisor handles how requests are executed
  - Hardware connects to physical card on host: Network/Disk I/O impacts performance
- SR-IOV - Single root/IO Virtualization
  - Network card presents as several "mini cards", unique as far as hardware is concerned, dedicated use by VM OS
  - In EC2 - Enhanced Networking, much better performance

## EC2 Architecture and Resilience
### Architecture
- VMs (OS + Resources)
- Instances run on EC2 Hosts
  - Shared (default) or Dedicated (pay for entire host)
  - AZ Resilent, Hosts = *1 AZ* (AZ fails, host fails, instances fail)
- Instance Host
  - Instance Store
  - Storage
  - Data Network
  - Primary elasctic network interface provisioned in subnet in VPC which maps to physical hardware on EC2 host
- Can connect to Elastic Block Store (EBS) - same AZ
  - allocate volumes of persistent storage
- Instance stays on host until maintenance, or until stopped and started; can't natively move between AZs
- Can never connect network interfaces or EBS in one AZ to an instance in another AZ
- Different instances share resrouces of host

### Uses
Traditional OS+Application Compute need
Long-Running Compute
Server style applications
Apps/Services that need either burst or steady-state load
Monolithic application stacks
Migrated application workloads or Disaster Recovery

## EC2 Instance Types 
### Chosing a type:
- Raw Resources (CPU, Memory, Storage)
- Resource Ratios
- Storage and Data Network Bandwidth (instance itself can be limiting factor)
- System Architecture / Vendor (ARM, AMD, Intel)
- Additional Features and Capabilities (e.g. GPU)

### Five Categories:
1. General Purpose - Default - Diverse workloads, equal resource ratio
2. Compute Optimized - Media Processing, Gaming, Machine Learning, etc.
3. Memory Optimized - Processing large in-memory datasets, some database workloads
4. Accerelrated Computing - Hardware GPU, field programmable gate arrays (FPGAs)
5. Storage Optimized - Sequential and Random IO - scale0out transactional databases, data warehousing, etc

### Decoding EC2 Types
example "Instance Type": R5dn.8xlarge
R - Instance Family (e.g. I T N R)
5 - Generation (version), generally always select most recent
dn - Additional Capabilities (a=AMD, n=network optimized, etc)
8xlarge - Instance Size (how much memory, CPU) - Nano, Micro, Small, XL, etc

Many instance types in each category
- T3, T3a - burstable instances, allocation of burst credits for peaks
- M5 - steady state workload
- C5 - compute optimized, media encoding, gaming
- and many more!

https://aws.amazon.com/ec2/instance-types/
https://ec2instances.info/

## EC2 SSH vs EC2 Instance Connect (Demo)
EC2... Key Pairs... Use A4L or Create
- RSA, .pem file, save key to local

Use 1-click deployment link, wait for complete
- Creates A4L VPC and an EC2 instance

EC2 Console... A4L-PublicEC2
- Security... Allows TCP (80) and SSH (22) from any IP (0.0.0.0/0 and ::/0)
- Right click, Connect, SSH Connect
- SSH in terminal using given command (make sure to chmod .pem file first - 644 too open, change to 400 `chmod 400 A4L.pem`)
- Make sure that security group of instance allows IP address

EC2 Instance Connect
- alternative to SSH
- Select correct user name
- No key needed, Identity of user needs permissions

Security Group... Inbound rules... Remove Source IP, change to "My IP", Save rule
- `exit` instance and re-connect, connection allowed from local IP
- Try EC2 instance connect, it's blocked - not actual originating connection from local machine, EC2 Connect Service is source, so it's blocked
- Add AWS IP ranges to allowed IPs in Inbound rules (https://ip-ranges.amazonaws.com/ip-ranges.json)

## Storage Refresher
Direct- or Local-attached: directly connected to EC2 Host
- Fast, but storage can be lost
- Alternative: Network-attached (ISCSI or fiber channel if local, AWS- EBS)

Ephemeral Storage- temporary
Persistent Storage- permanent, lives past lifetime of isntance 

### 3 Main Categories:
Block- Volume presented as collection of blocks. No structure (just uniquely addressable blocks). 
  - Mountable. Bootable. Hard disk or SSD or logical volume.
File Storage- Presented as file share... has structure.
  - Mountable. NOT bootable.
Object Storage- Flat structure. Collection of objects. (S3) Very scalable.
  - Not mountable. Not bootable.

### Storage Performance
I/O Block Size - size of wheeles of race care
  - kb or mb, size of block being written
I/O per/s - IOPS - speed of race car
  - Operations per second, network latency can affect this a lot
Throughput (MB/s) - top speed of rac car

IO block x IOPS =  Throughput
- Use right block size for a vendor, then maximize IOPS


## Elastic Block Storage (EBS) Service Architecture
Block storage- Allocation of a physical disk, a Volume
- Encrypted or unencrypted
- Create a file system on top- ext3/4, xfs, etc.
- Provisioned in 1 AZ (resilient in that AZ)
- Volume attached to One EC2 instance (at a time) over a storage network, can move between different hosts - PERSISTENT
- Snapshot (backup) into S3, can create volume from snapshot (maybe in diff AZ)
- Diff types, sizes, and perf profiles
- Billed based on GB/month metric

EBS - AZ based
e.g. withine us-east-1, can have different EBS in each AZ
EBS volumes separate from EC2 instances, with separate lifecycle
CANNOT communicate across AZ with storage
Data replicated within AZ, failure of AZ means faiilure of volume
  - S3 snapshot replicatea across ALL AZs

## EBS Volume Types - General Purpose SSD
GP2, GP3 (newer)
 ### GP2
- Small as 1GB, large as 16TB
- IO credit is 16KB
  - IOPS assume 16KB
  - 1 IOPS is 1 IO in 1s
- Bucket fills with 100 IO Credits per s, regardless of volume size
  - IO Credit Bucket Capacity - 5.4 million, fills at rate of baseline performance
  - Beyond 100 min, bucket fills with 3 IO credits per second, per GB of volume size (100GB volume gets 300 IO credits/s)
  - Burst up to 3,000 IOPS by depleting the bucket, can have small volume with periodic heavy workloads
- All volumes get an initial 5.4 million credits
- Max for GP2 - 16,000 IO credits per second (baseline performance)
- GP2 is currently default, elastic volume feature can change to GP3

### GP3
- removes credit bucket architecture
- 3,000 IOPS and 125 MiB/s standard
- GP3 is cheaper (~20%) vs GP2
- higher (4x) max throughput, up to 1,000 MB/s
- GP3 is like GP2 and IO1 had a baby


## EBS Volume Types - Provisioned IOPS

### Provisioned IOPS SSD (io 1/2)
Configurable independent of size of volume
*Super high performance (consistent low latency)*
Max 64,000 IOPS per volume (4x GP2/3)
  - with Block Express up to 256,000
Up to 1,000 MB/s throughput
  - with Block Express up to 4,000 MB/s

io1 50IOPS/GB MAX
io2 500IOPS/GB MAX
BlockExpress 1,000  IOPS/GB MAX

4GB - 16TB io1/2
4GB - 16TB BlockExpress

Per Instance Performance
- only most modern/largest instances support max performance
- io1 260,000 IOPS and  7,500 MB/s (will need multiple EBS)
- io2 a bit slower
- io2 BlockExpress same as io1

## EBS Volume Types - HDD-Based
HDD - moving bits, moving parts=slower

Types:
st1 - Throughput optimized, cheaper than GP2/3
-throughput/economy more important than IOPS
- 125GB - 16TB
- Max 500 IOPS
- Max 500 MB/s
- 40MB/s/TB base, 250 burst
- cost is concern, but need frequent access

sc1 - Cold HDD
- max economy for infrequent data access
- Max 250 IOPS
- Max 250MB/s
- 12MB/s/TB base, 80 burst (much slower)
- lowest cost EBS storage available
- for colder data requiring fewer scans per day

## Instance Store Volumes - Architecture
provides temporary block-level storage for your instance
- located on disks that are *physically attached to the host computer* - locally attached so *much higher perf than EBS*
- ideal for temporary storage of information that changes frequently, such as buffers, caches, scratch data, and other temporary content, or for data that is replicated across a fleet of instances, such as a load-balanced pool of web servers
- attached at launch, CANNOT attach after launch

An instance store consists of one or more instance store volumes exposed as block devices. The size of an instance store as well as the number of devices available varies by instance type.

The virtual devices for instance store volumes are ephemeral[0-23]. 
Instance types that support one instance store volume have ephemeral0. Instance types that support two instance store volumes have ephemeral0 and ephemeral1, and so on.

If an instance moves between hosts, data on ephemeral volumes is *lost*, new volume assigned
If a physical volume fails, data is lost, *ephemeral means temporary*
Different instance types have different types of instance store volumes

D3 instance is storage optimized
- 4.6 GB/s throughput
I3 - NVME SSD
- 16 GB/s throughput
- up to 2 million read IOPS

Exam Power-Up!
- Local on EC2 Host
- Can ONLY add at launch time
- Any data lost if instance moves, gets re-sized, or fails
- High Performance (highest in AWS)
- You pay for it anyway - included in instance cost
- TEMPORARY!

## Choosing Between the EC2 Instance Store and EBS *memorize this*
- Resilience - EBS (resilient within AZ)
- Storage isolated from instance lifecycle - EBS
- Resilience w/ App In-Built Replication - Depends...
- High performance needs - Depends...
- Super high performance needs - Instance store
- Cost - Instance store (since it's included)

- Cheap = ST1 or SC1
- Throughput/Streaming - ST1
- Boot Volume - NOT ST1 or SC1
- GP2/3 - up to 16,000 IOPS
- IO1/2 up to 64,000 IOPS (*new type up to 256,000 with larger instance types)
- RAID0 + EBS up to 260,000 IOPS (combined performance of all volumes, io1/2-BE/GP2/3)
- More than 260,000 IOPS - Instance store (trading persistence for performance)

## Snapshots, Restore, and Fast Snapshot Restore (FSR)
EBS Snapshots
- backup EBS volumes to S3
- protect against local storage system failure or AZ issues
- migrate data on EBS volumes between AZs

Snapshot: incremental colume copies to S3 (S3 is region resilient)
- first is full copy of *data* on the volume, can take some time
- future are incremental, faster and less space
- volumes can be created (restored) from snapshot, can be used EBS volumes between AZs or even regions

EBS Snapshots/Volume Performance
- New EBS VOlums = full performance immediately
- Snaps restore lazily - fetched gradually
- Requested blocks are fetched immediately
- You might force a read of all data immediately... before production usage
- Fast Snapshot Restore (FSR) - option on snapshot, immediate restore
  - up to 50 snaps per region, costs extra, can get same result by forcing read of every block (with `dd` or similar)
- GB-month metric
  - Used NOT allocated data, EBS doesn't charge for usused part of volume
  - Only changed data is stored

## DEMO - EBS Volumes (3 parts)
Create an EBS Volume
Mount it to an EC2 instance
Create and Mount a file system
Generate a test file
Migrate the volume to another EC2 instance in the same AZ
verify the file system and file are intact
Create a EBS Snapshot from the volume
Create a new EBS Volume in AZ-B
Verify the filesystem and file are intact
Copy the snapshot to another region
Create an EC2 instance with instance store volumes
Create a filesystem and test file
Restart instance and verify the file system is intact
Stop and Start the instance
Verify the file system is no longer present - new EC2 Host.

## EBS Encryption
EBS Volumes are block storage volumes presented over the network
- Default - no encryption (risk and physical attack vector)

### EBS Encryption
EC2 Host with EC2 Instance and attached Volume
Create encrypted volume: EBS uses KMS Key (default aws/ebs OR customer managed)
- Used to create encrypted data encryption key (DEK), sotred on volume
  - KMS Key -> DEK
- When instance launched, EBS asks KMS to encrypt DEK used for that volume, loaded into memory on EC2 host using volume
  - Key used to encrypt/decrypt - encrypted at rest
  - raw storage is encrypted
  - When EC2 changes hosts, DEK is discarded
  - Snapshot- samke DEK used for snapshot
  - Volumes from snapshot are ALSO encrypted
- Should use by default (no cost)

Exam!
- Accounts can be set to encrypt by default - default KMS key 
- Otherwise choose a KMS key to use
- Each volume uses 1 unique DEK, BUT ---
  - DEK is used for one volume and snapshots and future volumes from snapshot
- Can't remove encryption (without cloing data to unencrypted volume)
- OS isn't aware of the encryption, happens between EC2 host and volume - no performance loss
- Can use software/OS encryption if you want to maintain keys

## Network Interfaces, Instance IPs, and DNS
### EC2 Network and DNS Architecture
Instance- always starts with 1 Network Interface, Elastic Network Interface (ENI)
- can attach 1 or more separate ENIs in different subnets (but all in same AZ)
- Each ENI has:
  - Mac Address
  - Primary IPv4 Private IP
    - e.g. 10.16.0.10 -> ip-10-169-0-10-ec2.internal (DNS, resolvable inside VPC only)
  - 0 or more secondary IPs
  - 0 or 1 Public IPv4 Addresses
    - e.g. 3.89.7.136 (dynamic, will change with stop/start, restart won't change IP) -> ec2-3-89-7-136.compute-1.amazonaws.com (inside VPC, will resolve to private IP; outside VPC resolves to public IP)
    - 1 DNS name, traffic resolves differently internal and external
  - 1 elastic IP per private IPv4 address
    - if associated with primary ENI, removes public IPv4 (lose original dynamic public address)
  - 0 or more IPv6 addresses
  - Security Groups
  - Source/Destination Check (enable/disable), traffic discarded if doesn't meet conditions, needs to be off for NAT
- Secondary interfaces- same capabilities, except can be detached and moved

### Exam Power-Up!
Secondary ENI + MAC = Licensing
  - provsiion secondary ENI, can re-attach to another instance to move a license
Multi-homed (subnets Management and Data)
Different Security Groups - multiple interfaces, different SG on each
  - generally are working with primary ENI with SGs
OS - DOESN'T see public IPv4 (NAT performed by IG)
  - always confdigure on interface, not in OS
IPv4 Public IPs are DYNAMIC.... Stop and Start -> Changes
Public DNS = private IP in VPC, public IP everywhere else

## Manual Install of Wordpress on EC2 - DEMO
Will run Wordpress on single EC2 instance (so no high availability)
SubNet WEBA -> EC2 Instance (wrapped in Security Group) running Wordpress

## Amazon Machine Images (AMI)
Images of EC2, Create template with config, Create your own AMI
- Can be used to launch EC2 instance
- AWS or Community provided (e.g. RedHat CentOS, etc)
- Marketplace AMI (can include commercial software), extra cost includes license
- Regional - unique ID (e.g. ami-0a887e4503jd4873)
- Permissions (Public, Your Account, Specific Accounts)
- Can ceate and AMI from an EC2 instance you want to template

### Lifecycle
1. Launch
   - AMI -> Instance (Boot /dev/xvda, Data /dev/xvdf)
2. Configure
   - Add customizations (applications installed and configured, volume attached, etc)
3. Create Image
   - Instance + Volumes attached -> AMI (AMI ID, permissions)
   - EBS Snapshots are taken, referenced in AMI using "Block Device Mapping", links snapshot IDs and block device of original volume
4. Launch
   - New instance will have same EBS volume config as original
   - Volumes attached to new isntance with same device IDs
   - AMI stored in region, S3 snapshots regional

AMI is a container that references snapshots that are created from original volumes

Exam Power-Up!
- AMI = One Region, only works in that one region
- AMI Baking - creating an AMI from a configured instance + application
- An AMI CAN'T be edited... to modify, launch instance, update, and create a new AMI
- Can be copied between regions
- Permissions default = your account (can be private, public, or grant individual account access)
- Billed for capacity used by snapshots

## AMI - Demo
Install wordpress manually on EC2 .. you create a customized EC2 instance which has wordpress installed and configured right up to the 'create site' stage.
Additionally you improve the EC2 login screen by replacing the usual banned, with one provided by `cowsay` (It's animal themed !!)
Once the EC2 instance is ready - you will create an AMI from the customized source instance and use this to deploy a custom EC2 instance from this AMI.

## Copying and Sharing an AMI - Demo
Steps through the main points of copying an AMI between regions, details some encryption considerations and steps through the permissions model when looking at public, private and shared AMIs

## EC2 Purchase Options (Launch Types)
EC2 *purchase options*, explaining their mechanics and the type of situations they should be used in

On-Demand (default)
  - no specific pros or cons
  - Instances of diff sizes run on same EC2 hosts
    - multiple customer instances run on shared hardware
  - Per-second billing while an instance is running
    - Associated resources such as storage consume capacity, so bill regardless of isntance state
  - Good starting point for projects
  - No interruption
  - No capacity reservation
  - Predictable pricing, no upfront cost, no discount
  - Good for short term workloads and unknown workloads, and apps which can't be interrupted
Spot
  - Cheapest
  - Hosts might waste capacity on a host if not all used
  - Spot pricing is AWS selling unused EC2 host capacity for up to 90% discount
    - price is based on the spare capacity at a given time
    - price may go up to free up capacity
  - Never use spot for workloads which can't tolerate interruptions, instances might be terminated
  - Good fit- Non time critical
    - Anything which can be rerun, Burst capacity needs, Cost sensitive workloads, Anything stateless (state not stored, can handle disruption)
Reserved
  - Used in most large deployments, for long-term and consistent usage
  - Normal T3 - No reservation, Full per/s price
  - Matching instance - Reduced or no p/s price
  - Plan appropriately- possible to purchase and not use
  - Lock reservation to AZ - only benefit when launching in that AZ
    - Region reservation- can benefit any instance 
  - Partial covereage of larger instance- discount of partial component of larger instance
  - In return for commitment, resrources are cheaper (but pay whether or not used)
  - Term - 1 yr or 3 yrs, you pay for entire term
    - No upfront, some savings for agreeing to term, per/s fee, least discount
    - All upfront, entire 1 or 3 year term in advance, no per/s fee, greatest discount
    - Partial upfront, reduced per/s fee, less upfront costs, good compromise
Dedicated Host
  - Host entirely allocated to you
  - Number of cores, CPU, memory, network
  - No instance charges, pay only for host
  - Manage capacity
  - Might have software licensing based on sockets/cores
  - Host affinity- link instances to certain EC2 hosts (for licensing implications)
  - Reason to use- usually socket/core license requirements
Dedicated Instance
  - RUn on EC2 with other instances of your, no other customers use same hardware
  - You have host all ot yourself, but don't use whole thing
  - Hourly fee for any region where used (regardless of how many), plus fee per instance
  - Used when strict requirements that you can't share infra

## Reserved Instances - The Rest
Known as *Standard Reserved*
Good for known long-term usage that doesn't run constantly
- e.g. Batch processing daily for 5 hours starting at 23:00
  - reserve capacity, slighter cheaper than on-deman
- e.g. Weekly data- sales analysis every Friday for 24 hours
- e.g. 100 hours of EC2 per month
- Minimum purchase - 1,200 hours per year
- Minimum commitment - 1 yr
- Doesn't support all instance types or regions

### Capacity Reservations
Priority Order for delivering EC2 capacity
1 - Commitments, reserved purchases
2 - On demand requests
3 - Spot
Different from reserved instance - need to reserve capacity, but can't justify reserved instance

Options:
- Region reservation - billing discount for valid resources in an AZ in that region
  - don't reserve capacity with an AZ - which is risky during majot faults
- Zonal reservation - only apply to one AZ, provide billing discounts and capacity reservation in that AZ (only that AZ)

On-demand capacity reservations - can be booked to ensure you always have access to capacity in an AZ when you need it -  but at full on-demand price
  - No term limits, pay regardless of if you consume it
  - don't have same 1 or 3 year requirement as reserved instances
  - just reserving capacity, but don't benefit from cost reduction
  - at come point, look at reserved instance (more economical)

EC2 Savings Plan
- An hourly commitment for a 1 or 3 year term, reduction in cost
- Reservation of general compute $ amounts (save up to 66% vs on demand)
  - Valid for EC2, Fargate, and Lambda
- EC2 Savings Plan (only EC2, up to 72% savings)
- Products gave an on-demand rate and a Savings Plan rate
  - resource usage consumes savings plan commitment at reduced savings plan rate
    - after commitment - on-demand is used
    - Good choice when migrating away from EC2

## Instance Status Checks and Auto Recovery
Every instance in EC2 has 2 high level status checks, eventually moving to "2/2 checks passed"
1 - System Check
  - failure could indicate loss of power, loss of network connectivity, or other hardware issues (host)
2 - Instance Check
  - failure could indicate corrupt filesystem, incorrect networking config, or OS kernel issues

Might handle manually- restart, termineate, etc.... Or ask for Auto Recovery - moves to new host
- Status checks tab of instance... Actions.... Create status check alarm (trigger notification and/or actions like reboot, recover, stop, terminate)
  - Recover- restarts, might move to new host, won't save instance from AZ failure (won't work with instance store volumes, only EBS) - won't fix every problem

## Shutdown, Terminate, and Termination Protection - DEMO
Can Stop, reboot, terminate
- Must confirm terminate
- Can enable termination protection, unable to terminate
  - protects against accidental termination, and requires permissions to disable protection
  - can enable in CloudFormation
- Shutdown behavior settings- Stop (default) or Terminate

## Horizontal and Vertical Scaling
Scaling- systems grow and shrink based on demand/load

Vertical Scaling - Re-size EC2 instance
  - e.g. t3.large (2 vCPU, 8GB Mem) - Re-size to tx.xlarge or t3.2xlarge
  - there is downtime (requires reboot), restricts scaling to outage windows
  - larger instances carry a $ premium
  - there is an upper cap on performance (max instance size)
  - no application modification required
  - works for all applications - even Monoliths

Horizontal Scaling - Adds more instances
  - e.g. 1 instance -> 2, 4, or more
  - Copies of app running on each instance
  - Load balancer manages requests
  - Sessions are everything! (state of interaction)
    - requires application support OR off-host sessions (sessions stored somewhere else, servers are stateless)
  - no disruption while scaling
  - no real limits to scaling (can just keep adding)
  - less expensive - no large instance premium
  - more granular (vertical typically doubles size, horizontal can scale by smaller amounts)

## Instance Metdata - Theory and DEMO



