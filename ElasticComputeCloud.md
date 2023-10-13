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


