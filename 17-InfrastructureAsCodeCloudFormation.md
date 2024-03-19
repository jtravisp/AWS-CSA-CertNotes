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
- 

## CloudFormation Wait Conditions & cfn-signal
Test

## CloudFormation Nested Stacks

## CloudFormation Cross-Stack References

## CloudFormation Stack Sets

## CloudFormation Deletion Policy

## CloudFormation Stack Roles

## CloudFormation Init (CFN-INIT)

## CloudFormation cfn-hup

## CF wait conditions, cfnsignal, cfninit, and cfnhup - DEMO

## CloudFormation ChangeSets

## CloudFormation Custom Resources

## CloudFormation Custom Resources - DEMO
