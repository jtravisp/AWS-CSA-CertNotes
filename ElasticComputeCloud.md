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

## Choosing Between the EC2 Instance Store and EBS

