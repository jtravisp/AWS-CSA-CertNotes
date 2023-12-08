# Network Storage and Data Lifecycle

## EFS Architecture
AWS managed implementation of NFS which allows for the creation of shared 'filesystems' which can be mounted within multi EC2 instances.
EFS can play an essential part in building scalable and resilient systems.
Store media outside of EC2 instances

EFS is an implementation of NFSv4
EFS filesystems can be mounted in Linux
Shared between many EC2 instances
EBS is block storage, EFS is file storage
Private service, via mount targets inside a VPC
Can be accessed from on-prem- VPN or DX

VPC:
- AZ-A
- AZ-B
- EFS Filesystem -> Mount target inside each AZ
  - Put mount tragets inside multiple AZs for HA
- EC2 instances attach mount target in the same VPC
- VPC <-> VPN <-> On-prem infra

EFS:
- Linux Only
- General Purpose and Max I/O performance modes
- Gen Purpose = default for 99.9% of uses
- Bursting and Provisioned throughput modes
- Standard and Infrequent Access (IA) classes, IA for lower cost, Standard is default (mirror S3 classes)
- Lifecycle Policies can be used with classes

## Implementing EFS - DEMO
Use 1-click dployment for CF infra

Go to EFS, Create file system...
- Select name and VPC... Customize...
- Standard- multiple AZs, Automatic backups (yes for prod, no for demo)
- Lifecycle management options- transition to Infrequent Access
- Performance Mode- Gen Purpose most of the time, Mac I/O if absolutely needed
- Encryption (data at rest)- def yes fr prod, no for demo
- Network Settings
  - Mount Targets- AZ, Subnet ID, IP, Sec Group (delete defaults)
  - Sec group allows connections for alla ttached instances
- Go to file system, wait for mount targets to be ready

Go to EC2 Console
- Connect to A4L-EFSInstance A
  - will only see volumes directly attached to instance
  - Use commands below: Create folder /efs/wp-content, install amazon efs utils, edit fstab to mount EFS, replace "file-system-id" with your EFS filesystem-id 
  - `sudo mount /efs/wp-content` uses fstab to mount to that folder
- Connect to A4L-EFSInstance B
  - Install amazon efs utils, edit fstab, mount efs, check for file created from other instance

Commands:
```
# INSTANCE A

df -k
sudo mkdir -p /efs/wp-content
sudo dnf -y install amazon-efs-utils
cd /etc
sudo nano /etc/fstab

file-system-id:/ /efs/wp-content efs _netdev,tls,iam 0 0 

sudo mount /efs/wp-content
df -k
cd /efs/wp-content
sudo touch amazingtestfile.txt

# INSTANCE B

df -k
sudo dnf -y install amazon-efs-utils
sudo mkdir -p /efs/wp-content
sudo nano /etc/fstab
file-system-id:/ /efs/wp-content efs _netdev,tls,iam 0 0
sudo mount /efs/wp-content
ls -la
```

## Using EFS with Wordpress - DEMO
Evolve the Animals4life wordpress architecture by moving the wp-content (static media store) from the EC2 instance to an EFS based filesystem.
This will allow Wordpress to scale - we can move to an architecture where more than one Wordpress instance runs at once.
The experience you gain in this lesson while simple - will be the same experience used in much larger projects.

Deploy CF 1-click- Base Infra and 2 Wordpress deployments
  - Creates VPC, DB, and EFS in first deployment
  - Wordpress deployment uses infra from first deployment
    - Creates WP EC2, imports subnet and SG from first deployment
    - mounts EFS into EC2 instance

Create new WP post with images
Connect to WP EC2 instance
- Navigate to /var/www/html/wp-content/uploads/2023/11/
  - should see images uploaded
  - `df -k` shows filesystem, will see mounted NFS
Delete WP deployment stack, Create second WP stack
Open IP of new WP instance, will see that images are still there because they are loaded from NFS instance, not from EC2 instance

## AWS Backup
Use AWS Backup to centralize and automate data protection across AWS services and hybrid workloads. 
AWS Backup offers a cost-effective, *fully managed*, policy-based service that further simplifies data protection at scale. 
AWS Backup also helps you support your regulatory compliance or business policies for data protection. 
Together with AWS Organizations, you can use AWS Backup to centrally deploy data protection policies to configure, manage, and govern your backup activity across your company’s AWS accounts and resources.

Consolidate management into one place... across accounts and across regions
Supports a wide range of AWS products- EC2, EBS, EFS, Databases, S3

Compnents:
- Backup plans- frequency, window, lifecycle (when transitioned ot cold storage), vault, region copy
- Resources- what resrouces are backed up
- Vaults- backup destination (container)- assign KMS key for encryption
- Vault Lock- write-once, read-many (WORM), 72 hour cool off, then even AWS can't delete
- On-Demand- manual backups created as needed
- PITR- Point in Time Recovery
