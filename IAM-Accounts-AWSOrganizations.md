# IAM, Accounts, and AWS Organizations

## Identity Policies

IAM Policies attached to Identities
- Grants or denies access to features
- JSON
- 1 or more statements

Sid - Statement ID, optinal, identifies statement and what it does
Action- 1 or more actions, service:operation (list or *)
Resource- ind resources or *
Effect- allow or deny

```
{
	"Sid": "FullAccess",
	"Effect": "Allow",
	"Action": ["s3:*"],
	"Resource": ["*"]	
}
```

If allow/deny overlap- both processed,
- 1st priority- explicit denies
- 2nd- explicit allows (deny always wins)
- 3rd- default deny

Identities start off with no allows

Policies can come from IAM user, group membership, and resource policy
Remember Deny, Allow, Deny (above)

Inline policy- apply json to each account individually (not bext practice)
Managed policy- own object, create, then attach to identities to apply rights
	- re-usable
	- normal default opertaion rights in business
	- low management overhead, just change 1 json
	- Inline would be used for special exceptions
	
1. AWS Managed Policies
2. Custom Managed Policies


## IAM Users and ARNs

IAM Policies attached to Identities
IAM users are identity for anything requiring long-term AWS access- humans, applications, or service accounts

### Authentication v. Authentication
- Principal- needs to authenticate (U&P or access keys) and be authorized
- Authenticated Identity (after auth)
- AWS checks authorization of every action

### Amazon Resource Name (ARN)
uniquely identify resources
can always ID single resources (unique)
`arn:partition:service:region:account-id:resource-id`
`arn:partition:service:region:account-id:resource-type:resource-id`

actual bucket:
`arn:aws:s3:::catgifs`

anything in bucket, but not bucket itself
`arn:aws:s3:::catgifs/*`

- might need both for some actions
- ::: - you don't need to specify region or account because bucket name is golbally unique
- 5,000 max IAM users per account


## IAM Groups
Containers for users, manage users
(can't log in to a group)

Group: Devs
Group: QA
User can be member of multiple

Groups can have policies attached
User can also have policies
AWS merges all policies attached to user
Remember Deny-Allow-Deny rule
	1. Explicit deny
	2. Explicit allow
	3. Defauly deny

There is no default "all-users" group
No nesting!
300 groups/account, but can be increased

Policies attached to resources (like S3 bucket) can reference identity by ARN
	- Groups are NOT a true identity, can't be referenced as principal in a policy


## IAM Permission Control Demo
4n1m4l54L1f3

## IAM Roles - The Tech
Role- Identiy in AWS (other type IAM user)

IAM User- Single principal user (one person/principal)
Role- used by an unknown number of users/principals
	- generally used on a temporary basis
	- doesn't represent "you", represents access
	- "borrow" the permissions for a short time
	
IAM users- policies attached, control permissions of identity (inline or managed)
IAM roles
	- trust policy- who can assume role, even other AWS account or anon., facebook ID, twitter, google
		grant temp. credentials, like access keys but time limited
		must re-assume role after expiration
	- permissions policy
	
Roles can be referenced within resource policies
	- e.g. can be referenced in S# policy

Organization- AWS multi account management
	- roles allow login to one account, but access many

STS- Secure Token Service
	- operation used to assume role
	`sts:AssumeRole`

## IAM Roles- When to use
AWS services
- Lambda- function as a service
	- no permissions by default
	- needs way to get permissions
	- ***instead of hard-coding keys, create a ROLE*** hard-coding is security risk and is difficult to rotate keys
	- Lambda Execution Role, assumes role when function executed
	- sts:AssumeRole, STS generates temp. creds., used to access AWS resrouces based on role permission policy
	- might have many functions running at same time, role makes this easy

- Emergency or unusual situations
	- "break glass for key"
	- role can assume this function
	- gain temp. permissions based on role

- Adding AWS to existing environment
	- e.g. Active Directory- use SSO to use exisiting logins to access AWS
	- Roles re-use existing identities
	- Can't use external accounts directly
	- Allow IAM roles in AWS account to be assumed by external identity (like AD), temp roles assumed, credentials generated
	- "hidden" behind console UI
	- 5,000 IAM account limit, 
	- ID federation- small number of roles to manage

- ex. Ride sharing app, millions of users
	- DynamoDB
	- *Web Identity Federation*- uses IAM roles
	- Twitter, Google, etc.
	- Trust those identities, assume IAM role based on trust policy
	- use those credentials to access AWS resources like DB
	- no AWS creds stored in app, no chance of creds leak
	- customers already have the account
	- scales to millions

- Cross Account Access (Organizations)
	- use a role in partner account to obtain temp. creds, rather than creating many IAM users
	- give access to resources across account, or give access to whole account
	- e.g. assume role in general account to access all accounts (gen and prod, etc)

## Service-Linked Roles and PassRole
- IAM role linked to AWS service, pre-defined by service
- permissions a service needs to interact with other AWS services
- can't delete service linked role until it's not required
- double check resource names in yaml/json, not the same for every service

- can give user "PassRole" permissions, pass existing role into AWS service
- e.g. Bob passes a role into CloudFormation, creating resrources Bob alone does not have permissions for


## AWS Organizations
- allows larger businesses to manage AWS acounts in a cost-effective way
- 100s of accounts or more!

Standard account (not within org) - Create organization
  - This account becomes management account (previously master account)
  - Invite other existing standard account to org.
  - Accounts change from standard to "Member Account" 
  - Hierarchical:
    - Organization Root (just a container for AWS accounts- management account or member accounts)
      - can also contain other Organizaitonal Units (OUs)
      - can build complex nested account structure
      - NOT the same as "root user", which exists in every account
      - top level of the "tree"
  
Consolidated Billing- individual billing methods removed for member accounts
  - billing is passed through to Management Account (or Payer Account)
  - Single monthly bill for all accounts
  - More usage = cheaper rates, pooled resources good for billing

Service Control Policies (SCPs)- restrict what accounts can do

Can create new accounts within org. with valid email address

Best practice for logins and permissions: don't need IAM users in every account, user IAM Roles

Large orgs might keep management account clean and use other accounts for logins
	- Pattern is single AWS account with all identities
	- Large org. might use exisiting identitites using ID federation, using on-prem IDs
	- Can role switch to other accounts
    	- After logged in: role switch to another account, assuming a role


## Demo Time! - AWS Organizations
Use "general" account to invite "prod" account to organization

If you create an account in an org. a role is created allowing you to role switch
	- If you invite an account, you must manually add role
	- called "OrganizationAccountAcessRole"
	- Role switch into prod account (choose display name color, suggest "prod" and red)
	- Create dev account inside org (change role- "dev" and yellow)

## Service Control Policies
Restrict AWS accounts in an org.
Accounts:
- General
- Prod
- Dev
Next demo: add organizational unit- Prod and Dev

SCP (json)- attach to whole org, an OU, or an account
Inherit down org. tree, e.g. attached to whole account, then apply to everything
Can have nested OU- SCP affects everything below

*Management account is never affected by SCP*
- probably acoid using management account in prod

SCPs are account permission boundries
- limit what the account (*including account root user*) can do
- Root user always has 100% access to account, but is affected by SCP on entire account
- just a boundry, don't grant permissions
- Allow list vs Deny list
	- default is Deny list- everything allowed, no restrictions
	- you need to add any restrictions you want
	- e.g. DenyS3 policy
	- remember Deny-Allow-Deny- explicit deny always wins
	- default allow * covers new AWS services as they expand
	- Allow lists:
		- remove default FullAWSAccess policy
		- create allow policies, e.g. AllowS3EC2 policy
		- must explicitly add each allowed service
		- much higher admin overhead
		- easier to make a mistake and accidentally block services

SCP can deny access to something that is allowed in IAM policy
- Effective permissions are overlap between IAM and SCP

## SCP Demo

## CloudWatch Logs
Public service- usable from AWS or on-prem
Store, monitor, and access logging data (timestamp + logging data)
AWS Integrations- EC2, Lambda, R53, etc

Unified Cloudwatch Agent- anything outside of AWS services can log data into Cloudwatch logs

Can generate metrics based on logs- "metric filter"
	- scan logs constantly and create metrics triggering alarms

Regional:
	- Starting Point- Logging Sources inject data into CW logs
	- YYYYMMDDHHMMSS MESSAGE
	- Stored in "Log Stream"- data from one source
	- e.g. each log stream represents one EC2 instance
	- Log Groups- containers for different streams for same type of logging
		- stores config settings, applies to all log streams
	- Metric filters monitor log groups -> increment metric -> alarm

## Cloud Trail
Logs API actions that affect AWS accounts
	- Change security group, start EC2 instance, etc.

Every logged activity=Cloud Trail event
Stores *90 days* of events in Event History
	- enabled by default, no cost
	- To customize, create a "Trail"
	- 3 Types:
		Management
		Data
		Insight

Management Events: management events performaed on resources
	- Create EC2 isntance, create VPC, etc
Data Events: performed on/in a resource
	- Invoke Lambda, upload S3, etc

Cloud Trail "Trail"- provide config to CT
	- logs event in the region it is created in
	- Can set trail to 1 region OR all regions
	- most services log events in its region
	- Global services: IAM, STS, CloudFront- always log to us-east-1
		- services either log in their region or in us-east-1

Trail captures management and data events (if enabled, not default)
	- All-region or One-region
	- Can store logs in S3 bucket, compressed JSON logs (cahrged for S3 storage)

Can be integrated with CW Logs, can put logs in both S3 and CW Logs
	- CW logs gives more power than just S3 storage

Can create organizational trail, can store all info for all accounts in org

CT enabled by default in AWS accounts, but only 90 day 
	- Trails allow storage of data in better places
	- Management data only is default, Data events need to be enabled (extra cost)

Most AWS services data to local region, IAM, STS, CloudFront log data as global (to us-east-1), Trail must be enabled to capture global data

CloutTrail is NOT real time, delivers within 15 minutes, publishes multiple times per hours
	- takes a few minutes for data to arrive

## Cloud Trail Demo
Pricing:
	- 90 days history is free
	- 1 copy of mgmt events free in each region (1 Trail)
	- Addtl- $2/100k events
	- Logging data events- $.10/100k events

Set up org Trail- 1 in every account and every region (free)
CT generates a lot of data- might go over free tier

## AWS Control Tower
Allow quick and easy setup of multi-account environments
	- Orchestrates other AWS services, incl. AWS Organizations
	- Also IAM Identity center, Cloud Formation, and more
	- Adds features to AWS Orgs

Landing Zone- Well Architected multi-account environment
	- SSO/ID Federation, Centralized Logging and Auditing
	- Home Region (2.g. us-east-1)- always available
	- Security OU- Log Archive and Audit accounts
	- Sandbox OU- test/less rigid security
	- Uses IAM Identity Center (formerly AWS SSO)
	- Monitoring and Notifications
	- Service Catalog- end users can provision accounts

Guard Rails- detect/mandate rules/standard- all accounts
	- Mandatory, Strongly Recommended, Elective
	- Two ways:
		Preventive- stop you doing things
			- enforced or not enabled (e.g. allow/deny use of regions)
		Detective- compliance check, AWS Config rules to check if config matches best practice
			- clear, in violation, or not enabled

Account Factory- automates account creation
	- interact from CT console
	- provision accounts
	- Account Baseline (template)
	- Network Baseline (template)
	- Cloud Admin or End User (with appropriate permissions)
	- Guardrails- automatically added
	- Account admin given to a named user (IAM)- allow any org member to provision accounts
		- Account and network standard config
		- Accounts can be closed or repurposed
		- integrated with a business SDLC (stage of software development)

Dashboard- single page oversight of entire env.

Management Account
	- Control Tower
		CloudFormation
		Config -> SCP Guardrails
	- AWS Orgs
		Foundational OU (Security)
			Audit Account
				Audit info from Control Tower
				Can be used by 3rd party tools
				SNS, CloudWatch
			Log Archive Account (all logging for accounts in landing zone)
				AWS Config
				CloudTrail
		Custom OU (Sandbox)
	- SSO (IAM Identity Center)


