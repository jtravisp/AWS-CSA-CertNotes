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



