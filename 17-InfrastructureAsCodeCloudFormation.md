# Infrastructure as Code (CloudFormation)

## CloudFormation Physical & Logical Resources

CloudFormation defines logical resources within templates (using YAML or JSON). The logical resource defines the WHAT, and leaves the HOW up to the CFN product. A CFN stack creates a physical resource for every logical resource - updating or deleting them as a template changes.

- CF Template - YAML or JSON
- ...contains logical resources- the "WHAT"
- Templates are used to create Stacks
- templates used to create any number of stacks in each region- portable
- Stacks create physical resources from the logical
- If a stack's template is changed- physical reaources are also changed
- If a stack is deleted, normally the phyiscal resources are also deleted

YAML Template
```
Rsrources:
    Instance:
        Type: `AWS::EC2:Instance`
        Properties:
            ImageId: !Ref LetestAmiId
            InstanceType: "t3.micro"
```
etc.
-> CF Template -> CreateStack uses a template, parameters, and options to create a stack
-> CloudFormation Stack -> A Stack creates, updates, and deletes, physical resources based on logical resources in the template
-> T3 (AMI, SSH Key)
Once a logical resource moves to create_complete it can be queried for attributes of the physical resource within the template (e.g. physical machine ID)

- CF scans template and creates physical resrouces to match logical
- Change stack to modify physical resources
- Delete stack to also delete physical resources

## Simple NonPortable Template - DEMO

Understand why a non portable template is bad practice

CloudFormation Console
Use IDE to create template from scratch

```
Resources:
  Bucket:
    Type: 'AWS::S3::Bucket'
    Properties:
      BucketName: 'accatpics13333337'
  Instance:
    Type: 'AWS::EC2::Instance'
    Properties:
      InstanceType: "t2.micro"
      ImageId: 'ami-090fa75af13c156b4'
```

Upload YAML template to CF console, Create Stack
Look at Events to see if/why a Create fails
Wait for Create Complete state

Because S3 bucket name is explicitly named, can't use template again

Select a different region, create stack, upload same template
- no S3 bucket any more with that name
- image ID (AMI) does not exist, images are unique to region, another reason why template is not portable

## CloudFormation Template and Pseudo Parameters

- Template parameters accept input - console/CLI/API
- ...when a stack is created or updated
- Can be referenced from within logical resources
- ...influence physical resources and/or configuration
- Can be configured with defaults, AllowedValues, Min and Max length, and AllowedPatterns, NoEcho, and Type

Parameter Architecture
```
Parameters: 
    InstanceType:
        Type:String
        Default: `t3.micro`
        AllowedValues: 
            - `t3.micro`
            - `t3.medium`
            - `t3.large`
        Description: 'Pick a supported instance type.`
    InstanceAmiId: 
        Type: String
        Description: `AMI ID for Instances.`
```

- Parameters loaded, user chooses Type and inputs AMI ID
- Default or explicit values chosen -> Parameter values referenced within template logical resources -> CF provisions physical resources

Pseudo Parameters
- CF Template -> CF Stack
- AWS makes available paremeters that can be referenced even if not provided (injected by AWS into stack)
  - e.g. Region always matches stack creation region
  - AWS::StackName and AWS::StackId will match the specific being created and AWS::AccountId will be set by AWS to the actual account ID the stack is being created within
- like template parameters, but populated by AWS instead of human or process

## CloudFromation Intrinsic Functions

AWS CloudFormation provides several built-in functions that help you manage your stacks. Use intrinsic functions in your templates to assign values to properties that are not available until runtime.

Intrinsic Functions
- Ref & Fn::GetAtt
  - reference a value from one logical resource to another 
- Fn::Join & Fn::Split
- Fn::GetAZs & Fn::Select - get region and select element from list
- Conditions (Fn:If, And, Equals, Not, and Or)
- Fn::Base64 & Fn::Sub - convert to base64, sub values in text
- Fn::Cidr - auto config network ranges in CF template

Ref and Fn::GetAtt
- Logical Resource -> Stack (t3.micro) -> Physical resource
- e.g. `ImageId: !Ref LatestAmiId`
- `!GetAtt LogicalResource.Attribute` - retrieve any attribute associated with the resource

Fn::GetAZs and Fn::Select
- us-east-1 with 6 AZs, need to know name of AZs to pick one
- Hard coding is bad practice
- !GetAZs "us-east-1" or "" (current region)
- `AvailabilityZone: !Select [ 0, GetAZs '' ]`
- Select accepts a list and an index (0), dynamically refer to AZs in current region without explicitly reference identifiers

Fn::Join and Fn::Split
- provide delimiter and list of values, splits or joins

Fn::Base64 and Fn::Sub
- Provide user data in Base64 text, Base64 accepts normal text and outputs and encodes to Base64
- Sub allows replacements on variables  
  - `InstanceId : ${Instance.InstanceId}`
  - can't do self references, above is self reference, can't pass in attribute before its created

Fn::Cidr
- must provide CIDR range for VPC to use
- function references CIDR range of VPC
- Combine with Select and Get to 
- `CidrBlock: !Select [ "0", !Cidr [ !GetAtt VPC.CidrBlock, "16", "12" ]]`
- 16 is how many subnets to generate from the iput VPC range
- all based on parent VPC range

## CloudFormation Mappings

The optional Mappings section matches a key to a corresponding set of named values. For example, if you want to set values based on a region, you can create a mapping that uses the region name as a key and contains the values you want to specify for each specific region. You use the Fn::FindInMap intrinsic function to retrieve values in a map.

- Templates can contain a Mappings object
- ...which can contain many mappings
- ...which map keys to values, allowing lookups
- Can have one key, or Top and Second level
- mappings use `!FindInMap` intrinsic function
- Common use... retrieve AMi for given region and architecture
- Improve Template Portability

- Use !FindInMap to query a particular mapping in mappings are of template
- Provide at least one top level key
- `!FindInMap ["RegionMap", !Ref 'AWS:Region', "HVM64" ]`
  - Top level key is AWS::Region, Optional second level key is HVM64
  - value returned is AMI ID for us-east-1 with the HVM64 architecture

## CloudFormation Outputs

The optional Outputs section declares output values that you can import into other stacks (to create cross-stack references), return in response (to describe stack calls), or view on the AWS CloudFormation console. For example, you can output the S3 bucket name for a stack to make the bucket easier to find.

- Templates have an *optional* outputs section
- can declare values that will be visible in CLI, console UI
- *** accessible from a parent stack when using nesting
- *** can be exported, allowing cross-stack references

- Description: visible from CLI and console UI and passed to parent, best practice to provide description that's useful for someone else
- Value: determines what's exposed by stack after create complete  
  - can create URl with !Join 'https://' + !GetAtt Instance DnsName

## Template v2 - Portable - DEMO

Change template to be portable

```
Parameters:
  LatestAmiId:
    Description: "AMI for EC2"
    Type: 'AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>'
    Default: '/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'
Resources:
  Bucket:
    Type: 'AWS::S3::Bucket'
  Instance:
    Type: 'AWS::EC2::Instance'
    Properties:
      InstanceType: "t2.micro"
      ImageId: !Ref "LatestAmiId"
```

- non portable template can only be created once, S3 name is hard-coded
- Stage 1 - remove explicit bucket name, but AMI ID is still tied to current region
- Stage 2 - AMI ID is empty, user prompted on stack creation for AMI ID
- Stage 3 - retrieve latest Amazon Linux AMI, dynamically replaced for current region
  - SSM Parameter Store provides AMI ID

## CloudFormation Conditions

The optional Conditions section contains statements that define the circumstances under which entities are created or configured. You might use conditions when you want to reuse a template that can create resources in different contexts, such as a test environment versus a production environment. In your template, you can add an EnvironmentType input parameter, which accepts either prod or test as inputs. Conditions are evaluated based on predefined pseudo parameters or input parameter values that you specify when you create or update a stack. Within each condition, you can reference another condition, a parameter value, or a mapping. After you define all your conditions, you can associate them with resources and resource properties in the Resources and Outputs sections of a template

- created in optional 'Conditions' section of template
  Conditions are evaluated as True or False
- ...processed before resources are created
- Use the other instrinsic functions And, Equals, If, Not, Or
- ...associated with logical resources to control if they are created or not
- e.g. ONEAZ, TWOAZ, THREEAZ - how many AZs to create resources in
- e.g. PROD, DEV - control size of instance created

Example
- Template Parameter (dev, prod)
- Condition `IsProd: !Equals`  prd or not
- Conditions used within Resources
  - Resources have condition `Condition: IsProd` evaluates to True or False
  - resource only created if True
- can nest conditions, both condtions must evaluate to True

## CloudFormation DependsOn

With the DependsOn attribute you can specify that the creation of a specific resource follows another. When you add a DependsOn attribute to a resource, that resource is created only after the creation of the resource specified in theDependsOn attribute.

- CloudFormation tries to be efficient, doing things in parallel
- Create, Update, and Delete at the same time
- ...tries to determine depenedency order (VPC -> Subnet -> EC2)
- ...references or functions create these (if subnet references a VPC)
- DependsOn lets you explicitly define these
- ...If Resources B and C depend on A
- ...both wait for A to complete before starting (create complete)
- e.g. VPC + IGW, neither require the other
  - IGW Attachment requires both
  - `VpcId: !Ref VPC` and `InternetGatewayId: !Ref InternetGateway`
  - Ref creates dependency
- Elastic IP
  - associate with EC2 instance, requires attached IGW to VPC, but there is no dependency in the template
  - explicitly define dependency with `DependsOn`
  - `DependsOn: InternetGatewayAttachment`
  - this will be created after IGWAttachment and deleted before

## CloudFormation Wait Conditions & cfn-signal
CreationPolicy, WaitConditions and cfn-signal can all be used together to prevent the status if a resource from reaching create complete until AWS CloudFormation receives a specified number of success signals or the timeout period is exceeded.The cfn-signal helper script signals AWS CloudFormation to indicate whether Amazon EC2 instances have been successfully created or updated.

CF Provisioning
- Logical resources in the template -> Stack -> EC2 Instance
  - Match physical resources to template
- Logical Resource CREATE_COMPLETE = All Ok?
  - resource will show create complete even if bootstrap fails

CF Signal
- command included in AWS CFN Bootstrap package
- Config CF to Hold
- Wait for X number of success signals
- Wait for Timeout H:M:S for those signals (12 hours max)
- If signals received... CREATE_COMPLETE
- If failure signal received... creation fails 
- If timeout is reached... creation fails
- ...CreationPolicy or WaitCondition

CF CreationPolicy
- adds signal requirement (3) and timeout (15m)
  - waits after creation
  - ASG provisions 3 EC2 instances, each signalling once via cfn-signal
  - ASG template requires all 3 signals for CREATE_COMPLETE, otherwise CREATE_FAILED

CF WaitCondition
- can depend on other resources, other resources can depend on the WaitCondition
- relies on WaitHandle, generates a presigned USL for resource signals
- e.g. EC2 or External System that generates JSON passed back in signal response
  - can use !GetAtt on WaitCondition `{"Signal1":"SOme amazing thing has happened."}`

## CloudFormation Nested Stacks
Nested stacks allow for a hierarchy of related templates to be combined to form a single product
A root stack can contain and create nested stacks .. each of which can be passed parameters and provide back outputs.
Nested stacks should be used when the resources being provisioned share a lifecycle and are related.

A Stack...
- most projects use one isolated stack containing all resources
- resources created, updated, and deleted together - share a lifecycle
- Stack resource limites (500)
- Can't easily reuse resources e.g. a VPC
- Can't easily reference other stacks
- more complex projects use multiple stacks

Nested Stacks
- start with single Root Stack (Root and Parent Stack), created manually
  - Parent has its own nested stack
- can have Parameters and Outputs just like normal stack
- can have CF stack as a logical resource that creates stack of its own
  - includes `TemplateURL:`
- e.g. `VPCSTACK:`
- outputs of nested stack returned to root stack
  - can't refernece logcial resources, only outputs
- dependencies, e.g. ADSTACK DependsOn VPCSTACK
  - VPCSTACK.Outputs.XXX -> ADSTACK
  - APPSTACK DependsOn ADSTACK
- as each stack completed resource in root stack marked CREATE_COMPLETE
  - after all resources complete, root marked as CREATE_COMPLETE
- Allows templates to be resused because it's broken up, whole templates can be reused in other stacks
  - reusing the code, not the actual resources
- ***Use when the stacks from part of one solution - lifecycle linked***

Benefits
- overcome resource limit of single stack (2,500 max)
- Modular templates... code reuse
- Make the isntallation process easier...
- ...nested stacks created by the root stack
- *Use only when everything is lifecycle linked*, otherwise nested is wrong choice

## CloudFormation Cross-Stack References
Cross stack references allow one stack to reference another
Outputs in one stack reference logical resources or attributes in that stack
They can be exported, and then using the !ImportValue intrinsic function, referenced from another stack.

- Nested stacks- reuses code, but not resources (recreates all resources in the template)
- Want a Shared VPC?
  - CFN Stacks are designed to be isolated and self-contained

CF Cross-Stack References
- Outputs are normally not visible from other stacks
- Netsted stacks can reference them (but stack lifecycle is linked)
- e.g. testing an application, re-use the same VPC, gateways, etc
- Outputs can be exported... making them visible from other stacks
- Exports must have a unique name in the region
- `Fn::ImportValue` can be used instead of `Ref`

Architecture
- Shared VPC Stack
  - `Value: !Ref VPC`
  - Export SharedVPCID
  - value can be referenced in other stacks with `!ImportValue SharedVPCID`
  - import value into each stack you want to use it in
- Use in service-oriented and different lifecycles and Stack Reuse
- A Template is NOT a Stack
- Want to re-use a Stack (not a template)? Use Cross-Stack References

## CloudFormation Stack Sets
StackSets are a feature of CloudFormation allowing infrastructure to be deployed and managed across multiple regions and multiple accounts from a single location.
Additionally it adds a dynamic architecture - allowing automatic operations based on accounts being added or removed from the scope of a StackSet.

- Deploy CFN stacks across many accounts and regions
- StackSets are containers in an admin account
- ...contain stack instances... which reference stacks
  - container for an individual stack
- Stack instances and Stacks are in "target accounts" (other than Admin account)
- Each stack = 1 region in 1 account
- Security = self-managed or service-managed

Architecture
- Starts in Admin account, create here
  - e.g. StackSet "Bucket-o-Tron", creates single S3 bucket
  - Target Accounts
  - Permissions granted via self-managed IAM Roles or service-managed withing an ORG
  - StackSets gain access to Target Accounts and create stack instances (containers) and Stacks
- Each account - Resources created in Region 1 and Region 2
  - can use any number of accounts and regions

- Term: Concurrent accounts- how many AWS accounts can be used at same time
- Term: Failure Tolerance- amount of indiv. deployments that can fail before StackSet is considered Fail
- Term: Retain Stacks- remove stack instances from set, by default will delete stacks in target accounts, can set to retain (not default)
- Scenario: Enable AWS Config across accounts
- Scenario: AWS Config Rules- MFA, EIPS, EBS Encryption
- Scenario: Create IAM roles for cross-account access

## CloudFormation Deletion Policy
With the DeletionPolicy attribute you can preserve or (in some cases) backup a resource when its stack is deleted. You specify a DeletionPolicy attribute for each resource that you want to control. If a resource has no DeletionPolicy attribute, AWS CloudFormation deletes the resource by default.

- If you delete a logical resrouce from a template
- ...by defait, physical resource is deleted
- Can cause data loss
- With deletion policy, you can define on each resource...
- ....Delete (Default), Retain, or (if supported) Snapshot...
- ...EBS, ElastiCache, Neptune, RDS, Redshift
- Snapshots continue on past Stack lifetime- you have to clean up ($$)
- ONLY APPLIES TO DELETE... NOT REPLACE - deletion policy won't apply

- The Default- when logical resources are removed, physical also deleted
- Retain- Physical resources remain untouched when Stack logical resources removed
- Snapshot- (not supported for EC2)- EBS or RDS Snapshot

## CloudFormation Stack Roles
Stack roles allow an IAM role to be passed into the stack via PassRole
A stack uses this role, rather than the identity interacting with the stack to create, update and delete AWS resources.
It allows role separation and is a powerful security feature.

CFN Stack Roles
- When you create a stack- CFN creates physical resource
- CFN uses the permissions of the logged in identity
- ...which means you need permissions for AWS, this is a problem for many orgs
- CFN can assume a role to gain the permissions
- This lets you implement role separation
- The identity creating the stack doesn't need resource permissions...
- ...only `PassRole`

Architecture
- Gabby Account Admin
- Phil Account HelpDesk
- normally Phil would need permissions to create resources
- Gabby can create IAM role with permissions to create, update, and delete AWS resources (Phil can't assume role, only pass it into CFN)
- Role is attached to the stack and used for any operations
- Scenario- identity needs access not normally available? use Stack Role

## CloudFormation Init (CFN-INIT)
CloudFormationInit and cfn-init are tools which allow a desired state configuration management system to be implemented within CloudFormation

Use the AWS::CloudFormation::Init type to include metadata on an Amazon EC2 instance for the cfn-init helper script. If your template calls the cfn-init script, the script looks for resource metadata rooted in the AWS::CloudFormation::Init metadata key. cfn-init supports all metadata types for Linux systems & It supports some metadata types for Windows

- Provide config info to an EC2 instance
- Simple config management system
- cfn-init is natcive CFN feature
- Config directives stored in template
- AWS::CloudFormation::Init part of logical resource
- Procedural - HOW (Use data), how instance bootstraps itself
- ...vs Desired State - WHAT (cfn-init)
- less hassle than defining ins cript what should occur if state already exists
- `cfn-init` helper script- installed on EC2 OS (makes it so)

Architecture
- CFN Template creates EC2 instance
  - includes CFNInit
  - pass in user data
  - Template -> Stack -> Instance
    - UserData -> Instance
    - Variables StackId and AWS Region passed to cfn-init helper tool
    - performs defined config in logical resource
  - ConfigKey in CFNInit -> Packages, Groups, Users, Sources, Files, Commands, Services
    - typically one ConfigKey defining all

## CloudFormation cfn-hup
The cfn-hup helper is a daemon that detects changes in resource metadata and runs user-specified actions when a change is detected. This allows you to make configuration updates on your running Amazon EC2 instances through the UpdateStack API action.

- cfn-init is run once as part of bootstrapping (user data)
- ...if CloudFormation::Init is updated, it isn't rerun
- cfn-hup helper is a daemon which can be installed
- ...it detects changes in resource metadata
- ...running configurable actions when a change is detected
- Use tools together
  - UpdateStack -> updated config on EC2 instances

CFN Template
  - packages, groups, users, sources, etc
  - Change template - UpdateStack operation
  - cfn-hup checks metadata periodically
  - when updated, calls cfn-init
  - cfn-init applies new config

## CF wait conditions, cfnsignal, cfninit, and cfnhup - DEMO

Use YAML files to create CFN resources
- Copy EC2 instance IP, doesn't load
- `sleep 300` to wait 5 minutes, problem is that CFN has no awareness, can be a problem if you have lengthy bootstrap process
- change "message" parameter updates stack, restarts instance, doesn't update instance because user data only applied on 1st launch
- Delete stack, look at user data with signal
  - adds cfn-signal, signals to stack if successful or not
  - stack will show Received Success, gives time for bootstrapping before shows CREATE_COMPLETE
- Delete stack, look at cfn-init with signal
  - adds `Metadata:` + `AWS::CloudFormation::Init`
  - pass in stack, resource, and region, applies config (commands, services, etc)
  - Click on resources, connect to instance
    - check /var/log to check logs, `cloud-init-output.log` 
      - permission denied? use `sudo cat` to view log
      - shows output of user data process of bootstrapping process
      - `cfn-init-cmd.log` shows what's done by cfn-init command
      - `cfn-init.log` shows all actions completed by cfn-init process
    - Stack still won't update config on changes
- Delete stack, look at stack that adds- cfn-hup utility
  - define triggers (on stack update) and actions (re-run cfn-init)
  - find `cfn-hup.log`
  - `sudo tail -f cfn-hup.log` to view last set of logs and monitor constantly
  - change Message parameter of stack, watch for changes, should re-run cfn-init

## CloudFormation ChangeSets
When you need to update a stack, understanding how your changes will affect running resources before you implement them can help you update stacks with confidence. Change sets allow you to preview how proposed changes to a stack might impact your running resources, for example, whether your changes will delete or replace any critical resources, AWS CloudFormation makes the changes to your stack only when you decide to execute the change set, allowing you to decide whether to proceed with your proposed changes or explore other changes by creating another change set.

- Template -> Stack -> Physical Resources (CREATE)
- Stack (Delete) -> DELETE Physical Resources
- v2 Template -> Existing Stack -> Resources CHANGE
- No interruption, Some interruption, Replacement (new copy, old removed, possible data loss)
- Change Sets let you preview changes (A Change Set)
- ...multiple diff versions (lots of change sets)

Architecture
- Template to create 3 buckets
  - didn't mean to create one
  - create new template without extra bucket, physical resource gets deleted
- Using change sets, create Stack B ChangeSet Template 2

Demo
- Go to CFN console
- Template 1 creates 3 buckets, Template 2 creates 2
- Create stack with Template 1
  - see 4 buckets in Resources
- Go to Change Sets tab or Stack actions... create change set
  - Repalce current template, upload template 2
  - Create change set (does not update original stack)
- To use, click Change Sets tab to see changes that would be made
  - `Execute` to update stack with changes

## CloudFormation Custom Resources
Custom resources enable you to write custom provisioning logic in templates that AWS CloudFormation runs anytime you create, update (if you changed the custom resource), or delete stacks

- Logical Resources in a template - WHAT you want
- CFN uses them to CREATE, UPDATE, and DELETE physical resources
- CFN doesn't support everything...
- Custom resources let CFN integrate with anything it doesn't yet, or doesn't natively support
  - e.g. populate an S3 bucket with objects; delete objects from bucket; request config info from external system, provision non-AWS resources
- Passes data to something, gets data back from something (maybe SNS or Lambda)
  - Lambda can respond with pass/fail and pass back data

Architecture
- without Custom Resource:
  - Template -> Stack -> S3 Bucket
  - User adds objects, now out of sync with template, stack delete would fail because bucket isn't empty
- with Custom Resource:
  - Template -> Stack -> S3 Bucket
    - Template has CustomLambda, passed event data (anything given to resource)
    - Lambda sends objects to bucket
    - sends response URL, stack moves to CREATE_COMPLETE
  - User adds objects to bucket
  - STACK_DELETE starts process of delete
    - CFN knows custom resource depends on bucket, reverses dependency
    - deletes objects using Lambda function
    - Lambda signals to CFN with response URL that operation was success
    - no further dependencies, so stack deletes

## CloudFormation Custom Resources - DEMO

- see `17-customresaource.yaml`
  - invokes Python Lambda function
- Create S3 resources without custom resource, add files
  - Delete the stack, fails because bucket not empty
  - Delete stack after emptying bucket, success
- Create S3 resrources with custom resource
  - Lambda function copies objects when bucket created and deletes when bucket deleted
  - different actions depending on CREATE or DELETE
  - `Custom::S3Objects` ServiceToken is Amazon resource name for Lambda function
    - Source Bucket and Source Prefix define where objects to be copied are located
  - Creates stack, creates bucket (dependency order in template, implicit because bucket references other resources)
  - new bucket will already have 3 images inside
  - Add more objects to bucket... Delete stack
    - Lambda Custom Resource will delete objects inside bucket
