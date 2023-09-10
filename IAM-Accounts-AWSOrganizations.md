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
