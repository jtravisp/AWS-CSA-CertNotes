# Advanced EC2

## Bootstrapping EC2 using User Data
Bootstrap in certain config in EC2 instance
Bootstrapping- allow system to self-configure or launch with configs
Bootstrapping allows *EC2 Build Automation*
User Data- Accessed via the meta-data IP
    - http://169.254.169.254/latest/user-data
    - Anything you pass in is executed by instance OS, just once at launch
EC2 doesn't interpret or validate data, just passes to OS, runs as root user

AMI -> Instance (with EBS volume attached based on AMI mapping) <- User Data from EC2
    - Instance executes User Data -> Running/Ready for Service OR Bad Config (still passes status checks)

User Data is opaque to EC2 - it's just a block of data
It's NOT secure - don't use for passwords or long-term credentials
Limited to 16KB in size
    - larger? use script to download data
Can be modified when instance stopped...
But only executed once at launch

## Boot-Time-To-Service-Time
Includes time to provision + updates/installations
AMI -> Minutes to Instance -> Post Launch Time (minutes to hours)
    - Bootstrapping automates post launch time
AMI Bake (frontload work) -> Ami -> Minutes to Instance
- Maybe AMI bake in installation, Bootstrap config (optimal)

## Bootstrapping Wordpress Installation - DEMO
bootstrap two EC2 instances with WordPress and the 'cowsay' login banner customizations.
The first, directly using User Data via the console UI
the second, using CloudFormation
You will gain experience of bootstrapping, and see how to diagnose the process - by querying userdata passed into the instance using curl, and secondly by reviewing log files.

Get token to authenticate to metadata service, get metadata of instance, then userdata:
```
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/
curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/user-data/
```

Bootstrap userdata.txt:
```
#!/bin/bash -xe

# STEP 1 - Setpassword & DB Variables
DBName='a4lwordpress'
DBUser='a4lwordpress'
DBPassword='4n1m4l$4L1f3'
DBRootPassword='4n1m4l$4L1f3'

# STEP 2 - Install system software - including Web and DB
dnf install wget php-mysqlnd httpd php-fpm php-mysqli mariadb105-server php-json php php-devel cowsay -y
# STEP 3 - Web and DB Servers Online - and set to startup
systemctl enable httpd
systemctl enable mariadb
systemctl start httpd
systemctl start mariadb
# STEP 4 - Set Mariadb Root Password
mysqladmin -u root password $DBRootPassword
# STEP 5 - Install Wordpress
wget http://wordpress.org/latest.tar.gz -P /var/www/html
cd /var/www/html
tar -zxvf latest.tar.gz
cp -rvf wordpress/* .
rm -R wordpress
rm latest.tar.gz
# STEP 6 - Configure Wordpress
cp ./wp-config-sample.php ./wp-config.php
sed -i "s/'database_name_here'/'$DBName'/g" wp-config.php
sed -i "s/'username_here'/'$DBUser'/g" wp-config.php
sed -i "s/'password_here'/'$DBPassword'/g" wp-config.php
# Step 6a - permissions 
usermod -a -G apache ec2-user   
chown -R ec2-user:apache /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} \;
find /var/www -type f -exec chmod 0664 {} \;
# STEP 7 Create Wordpress DB
echo "CREATE DATABASE $DBName;" >> /tmp/db.setup
echo "CREATE USER '$DBUser'@'localhost' IDENTIFIED BY '$DBPassword';" >> /tmp/db.setup
echo "GRANT ALL ON $DBName.* TO '$DBUser'@'localhost';" >> /tmp/db.setup
echo "FLUSH PRIVILEGES;" >> /tmp/db.setup
mysql -u root --password=$DBRootPassword < /tmp/db.setup
sudo rm /tmp/db.setup
# STEP 8 COWSAY
echo "#!/bin/sh" > /etc/update-motd.d/40-cow
echo 'cowsay "Amazon Linux 2023 AMI - Animals4Life"' >> /etc/update-motd.d/40-cow
chmod 755 /etc/update-motd.d/40-cow
update-motd
```

You can provide userdata in CloudFormation template!

## Enhanced Bootstrapping with CFN-INIT
AWS::CloudFormation::Init
- cfn-init - helper script installed on EC2 OS 
    - simple configuration management system
    - procedural (user data) vs desired state (cfn-init)
- Packages, Groups, Users, Sources, Files, Command, and Services
- Passed into instance as part of user data
- Provided with directives via Metadata and AWS::CloudFormation::Init on a CFN resource

cfn-init
Template (logical resource EC2instance inside) -> Stack -> Instance
"Desired State System" - will implement desired state from CloudFormation template

```
AWS::CloudFormation::Init:
    configSets: ...
    install_cfn: ...
    etc
```
 UserData only works once when instance launched

 CreationPolicy and Signals
    - cfn-signal
    - CloudFormation doesn't know if UserData doesn't work
    - CreationPolicy added to lgocial resource in CF
    - CF waits for signal from resource, cfn-signal given stack name, resource name, and region
      - `-e $?` - state of previous command, cfn-signal reports to CF success or not of cfn-init bootstrapping
      - timeout value in template, e.g. `Timeout: PT15M`

## CFN-INIT and CFN Creation Policies - DEMO
Bootstrap with CreationPolicy instead of user data

```
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/
curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/user-data/
```
```
AWS::CloudFormation::Init:
    configSets:
        wordpress_install:
            - install_cfn
            - software_install
            ...
    install_cfn:
        files:
            ...
            ...
```
Process can cope with stack updates, re-runs CFN update if changes occur, cfn hook

## EC2 Instance Roles and Profile
Service can assume role
EC2 Instance role- anything running in instance has that role's permissions
Permissions Policy with S3.* -> IAM Role -> Profile attached to instance (temp creds delivered via instance meta-data)
    - Creds always renewed before they expire
- IAM Role allows EC2 Service to assume it

InstanceProfile 0 wrapper around IAM role
    - in console - IP created with same name
    - CF, CLI - create ceparately
    - The InstanceProfile is attached to instance (not the instance role)

### Key Points
Creds are inside meta-data
IAM/Security-credentials/role-name
Auto rotated- always valid
Should always be used rather than adding access keys into instance
CLI tools will use ROLE credentials automatically

## Using EC2 Instance Roles - DEMO
Create an EC2 Instance Role, apply it to an EC2 instance and learn how to interact with the credentials this generates within the EC2 instance metadata.

```
aws s3 ls
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/A4LInstanceRole
```

AWS CLI creds precedence: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html#cli-configure-quickstart-precedence

Stack: VPC, EC2 Instance
Initially no config or attached role - can't interact with AWS 
    - could use `aws configure`, but not best practice
    - Go to IAM console, Create IAM role for instance - Type- AWS service, EC2
    - Permissions- S3ReadOnly
    - Role + InstanceProfile with same name created together
    - EC2 Console - Right click, Security, Modify IAM role... Choose newly created role
      - Confirm in instance security tab
    - Connect to instance, now have AWS credentials, e.g. `aws s3 ls`
      - will use role name
      - credentials renewed automatically

## SSM Parameter Store
AWS Systems Manager Parameter Store
Don't pass secrets into EC2 using UserData!

- Storage for config and secrets
- String, StringList, and SecureString
- License cods, databse strings, full configs and passwords
- Hierarchies and Versioning
- Plaintext and Ciphertext (uses KMS)
- Public parameters - Latest AMIs per region

Public service
App, Lambda, EC2 -> SSM-PS (using IAM) -> KMS
- myDBpassword
- /wordpress/
  - DBUser
  - DBPassword
Flexible permissions- singe parameter or whoel tree

## Parameter Store - DEMO
Create some Parameters in the Parameter Store and interact with them via the command line - using individual parameter operations and accessing via paths.
Go to "Systems Manager", then "Parameter Store", Create Parameter
- Standard is default (10k or less)
- / establishes hierarchy, e.g. /my-cat-app/dgstring
- Use default KMS key

```
# CREATE PARAMETERS

/my-cat-app/dbstring        db.allthecats.com:3306
/my-cat-app/dbuser          bosscat
/my-cat-app/dbpassword      amazingsecretpassword1337 (encrypted)
/my-dog-app/dbstring        db.ifwereallymusthavedogs.com:3306
/rate-my-lizard/dbstring    db.thisisprettyrandom.com:3306

# GET PARAMETERS (if using cloudshell)
aws ssm get-parameters --names /rate-my-lizard/dbstring 
aws ssm get-parameters --names /my-dog-app/dbstring 
aws ssm get-parameters --names /my-cat-app/dbstring 
aws ssm get-parameters-by-path --path /my-cat-app/ 
aws ssm get-parameters-by-path --path /my-cat-app/ --with-decryption
```

CloudShell- AWS CLI from web console instead of local machine
aws ssm get-parameters returns json with name, type, value, last modified, ARN, datatype
With hierarchical structure, can retrieve multiple at once
If user has permissions, can ask for decryption with `--with-decryption`

## System and Applcation Logging on EC2
CloudWatch- performance and reliability aspect of EC2 (external only by default)

### Summary
Logging on EC2
- CloudWatch is for metrics
- Cloudwatch Logs is for logging
- Neither natively capture *data instide an instance*
- CloudWatch Agent is required
- ...plus configuration and permissions

EC2 Instanace (e.g. Wordpress) <- CloudWatch Agent <- Agent Config
- Creat IAM with permissions to interact with CW logs
- Log group for every log file -> CW Logs
- Single instance? Manual, Many? Automate with CF
- Use Paramter Store to store agent config as parameter

## Logging and Metrics with CloudWatch Agent (20m)


## EC2 Placement Groups


## Dedicated Hosts


## Enhanced Networking and EBS Optimized


