# Serverless and Application Services

## Architecture Deep Dive
Event Driven Architecture Example
YouTube
    - User -> Upload Video -> App -> Processing (diff resolutions, playlists, etc)
    - Traditional- monolithic, Upload, Processing, Store and Manage all together in one app
      - fail together, scale together, bill together
      - Monolithic is least cost effective
    - Tiered architecture- separates components, coupled together
      - scale independently
      - internal LB between tiers, additional instances can be added, managed by LBs, now HA
      - Tiers are still coupled, require each other to exist, each tier has to be running something for the app to function

Evolving with Queues
    - Accepts messages, messges can be received or polled off queue
    - first in, first out (FIFO) most common
    - Upload goes to S3 with a message to queue with details
    - Upload tier doesn't require an immediate response from next tier, asynch communication
    - Queue- Auto Scaling Group (e.g. Min:0 Desired:0 Max:1337)
      - instances provisioned, start polling queue, receive messages at front of queue
      - jobs processed and deleted, ASG may scale back when queue gets shorts
      - Queue decouples tiers

Microservice Architecture- collection of micrososervices
    - e.g. Process, Upload, Store and Manages
    - Procuser, Consumer, or Both- produce or consume events

Event Driven Architecture
    - Producer- create events
    - Consumer- ready and waiting for events to occur, take an action
    - components can be one or both
    - Best practice- event router (with an event bus)- constant flow of information, router delivers to consumers
- No constant running or waiting
- Producers generate events, actions taken based on event
- ...clicks, error, criteria met, uploads, actions
- Events are delivered to Consumers
- ...actions taken, system returns to waiting

## AWS Lambda
Function as a Service (FaaS)- short running and focused
- Lambda Function- a piece of code Lambda runs
- Functions use a runtime (e.g. Python 3.8)
- Functions are loaded and run in a runtime environment
- Environment has a direct memory (indirect CPU) allocation
- Billed for duration of execution
- part of Serverless architectures

Definte Lambda Function (code + wrappings and config)
- Define language, provide deployment package, downlaoded and executed in environment
  - Python, Ruby, Java, Go, C#, NodeJS, etc, also custom
  - Docker = Think not Lambda, referes to traditional containerized computing (like ECS)
  - can use container images with Lambda
  - Custom runtimes allows Rust using layers
  - runtime selected when creating function
  - Functions are stateless (no data left over previous invocation)
  - Define resources used, memory 128-10240MB mnemory, CPU scales with memory
  - 512MB storage available at /tmp, up to 10240MB available
  - can run for up to 900s (15m), beyond this can't use Lambda

Common Uses
- Serverless Apps (S3, API Gateway, Lambda)
- File Processing (S3, S3 Events, Lambda)
- Database Triggers (DynamoDB, Streams, Lambda)
- Serverless CRON (EventBridge/CWEvents + Lambda)
- Realtime Stream Data Processing (Kinesis + Lambda)

Two Networking Modes:
- Public (default)
  - App running in a VPC- Aurora DB, EC2, EFS
  - by default Lambda functions given public networking, can access public AWS services and the public internet
  - SQS, Dynamo DB -> Lambda -> IMDB Moveies and TV Shows
  - Public networking offers best performance because *no customer specific VPC networking is required*
    - no access to services in VPC (unless services have public addressing and security rules)
  - public is most common
- Private
  - Lambda runs inside private subnet with app infra
  - obey all VPC networking rules
  - can't access resources outside VPC, unless networking config exists to allow
  - Treat Private Lambda like anything else running in a VPC, can use a GW endpoint to leave
    - NAT GW -> IGW
    - NatGW and IGW are required for VPC Lambdas to access internet resources
  - Needs ec2 network permissions
  - AWS [AWS Lambda Service VPC] each function, elastic network interface -> [A4LVPC/CustomerVPC]
    - takes time, adds delay, doesn't scale well (parallel functions) (OLD WAY)
    - New Way- Lambdas -> unique SG/Subnets -> one network interface, functions use same elastic network interface
      - created when you configure Lambda function, done once at creation, not required every time its invoked

Security
- Function Code in a Runtime Environment (e.g. Python 3.8)
- must be provided an Execution Role (gains permissions of that role)
- Trust Policy trusts Lambda, same as EC2 instance role
- e.g. Permissions to load from DynamoDB and store in S3
- Lambda resource policy controls WHAT services and accounts can INVOKE Lambda functions
  - allows external accounts to use function
  - resource policy changes via CLI/API, NOT console UI
- Lambda execution roles are IAM roles attached to Lambda functions which control PERMISSIONS the function receives

Logging
- uses CloudWatch, CloudWatch Logs, and X-Ray
- Logs from Lambda executions - CloudWatch Logs
- Metrics- invocation success/failure, retries, latency... stored in CloudWatch
- Lambda can be integrated with X-Ray for distributed tracing
- CloudWatch Logs requires permissions via Execution Role

Invocation
- Synchronous
  - CLI/API -> Invoke function
    - passing in data and wait for response
    - Lambda -> CLI/API
  - Clients -> API Gateway -> proxied to lambda function -> lambda responds or fails -> repsonse to client
  - Errors or retries have to be handled within the client
- Asynchronous- typically used when AWS services invoke functions
  - upload pic to bucket, triggers invocation
  - S3 doesn't wait on response, the event is generated and S3 stops tracking
  - Lambda responsible for and re-processing if event fails
  - will retry between 0 and 2 times
  - function needs to be *idempotent reprocessing* a result should have the same end state
    - e.g. 10 + 10 vs. set new value at 20, rerunning function has differnt results
    - make sure function code isn't additive or subtractive, just sets desired end state
  - Events can be sent to Dead Letter Queues (DLQ) after repeated failed processing
  - supports destinations (SQS, SNS, Lambda, and EventBridge) where successful or failed events can be sent
- Event Source mappings
  - Used on streams or queues which don't support event generation to invoke lambda (Kinesis, DynamoDB, SQS)
  - Producers (Telemetry) -> Kinesis Data Stream
    - Event Source Mapping looking for data (Source Batch) -> Event Source Mapping <-> Event Batch <-> Lambda Function
  - Source service isn't delivering an event, Source mapping is reading from source
    - uses permissions from Lambda execution role to access source service
    - Ececution role needs acess to source service, even though it doesn't directly read service
  - Event Source Mapping -> SQS Queues or SNS Topics, can be used for any discarded failed event batches

Versions
- can define specific versions of a function
- version is the code + the config of the function
- a version is immutable - it never changes once published and has its own Amazon Resource Name
- $Latest - points at the altest version
- Aliases (Dev, Stage, Prod) point at a version- can be changed

Lambda Start-Up Times
- Code runs in runtime environment ("execution context")- container that runs your code
- Cold Start (100s of milliseconds): Invocation -> Context configured, hardware, runtimes downloaded/installed, deployment package installed 
  - Invocation without much gap, use same Execution Context (Warm Start)
  - ~1-2ms
- if used infrequently contexts will be removed
- Concurrent executions will use multiple (potentially new) contexts
- Provisioned concurrency can be used- AWS will create and keep X contects warm and ready to use, improving start speeds
- anytihng defined withing Lambda function handler, only available inside that invocation
  - must be fine with recreating everything, stateless, clean environment

## CloutWatchEvents and EventBridge
CloudWatch Events and EventBridge have visibility over events generated by supported AWS services within an account.
They can monitor the default account event bus - and pattern match events flowing through and deliver these events to multiple targets.
They are also the source of scheduled events which can perform certain actions at certain times of day, days of the week, or multiple combinations of both - using the Unix CRON time expression format.
Both services are one way how event driven architectures can be implemented within AWS.

EventBridge can handle events from third parties, AWS encouraging migration to EventBridge

Key Concepts
- If X happens, or at Y time(s)... do Z (UNIX CRON format)
- EventBridge is... CloudWatch Events v2, superset of CWE features, use EventBridge by default!
- A default Event bus for the accoutn,stream of events that occur
- ...CW Events this is the only bus (implicit), look for events, send to targets
- EB can have additional event buses
- Rules match incoming events.... (or schedules)
- Routes the events to 1+ Targets... e.g. Lambda

Events
- Default Event Bus
  - EC2 change state -> Event genereated, runs through bus -> EB monitors (Event Pattern Rule, Schedule Rule (rule executed based on time)) -> Target (e.g. Lambda)
  - Events are JSON, includes instance changing, what changed to, date, time

## Automated EC2 Control using Lambda and Events - DEMO (32m)
Using Lambda for some simple account management tasks.
1-Click Deployment Stack
Create Lambda Execution Role:
IAM Consonle... Roles... Create Role...
  - EWS Service - Lambda
  - Create managed policy, use JSON below, "Lambda Start and Stop"

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Start*",
        "ec2:Stop*"
      ],
      "Resource": "*"
    }
  ]
}
```

Add permissions to role, call role "EC2StartStopLambdaRole"
  - Lambda assumes role to acquire permissions

Go to EC2
  - Stack isntances running (2), make note of instance ID
Go to Lambda
  - Create function... from scratch... "EC2Stop"... Runtime: Python 3.9
  - Change role to newly created role... Create function
  - Right click function, Open, Replace with Lambda stop code below
  - accepts list of EC2 instance from env variable, ec2.stop_instance call to stop instances
  - Deploy

lambda_instance_stop.py
```
import boto3
import os
import json

region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)

def lambda_handler(event, context):
    instances=os.environ['EC2_INSTANCES'].split(",")
    ec2.stop_instances(InstanceIds=instances)
    print('stopped instances: ' + str(instances))
```

Configuration... Env Variable... Create...
  - Key: EC2_INSTANCES, Value: Instance IDs comma separated
  - Test tab, provide example event data, test should stop instances

Create another function for EC2 Start
  - same as stop but in reverse
  - Test to create manual invocation

Event Driven Workflow!
  - Create Lambda function... "EC2Protect"... Python 3.9... LambdaIAM role
  - function accepts event data, determines which instance is stopped, starts it back up

```
import boto3
import os
import json

region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))
    instances=[ event['detail']['instance-id'] ]
    ec2.start_instances(InstanceIds=instances)
    print ('Protected instance stopped - starting up instance: '+str(instances))
```

EventBridge- Create rule... event source AWS events...
  - Select EC2 service, EC2 Instance State-Change Notification
  - Generate sample event for state-change, provides JSON
  - Add instance ID for EC2 isntance
  - Select targets... (every target gets event at same time)... EC2Protect Lambda function... Create rule
  - rule monitors default event bus of account
- Stop the instance, event generated (instance state change), rule sees instance ID, invokes lambda function
  - instance moved to stop, rule triggered, lambda invoked, started instance
  - Open CloudWatch logs, Log groups, log group with same name as lambda function, see output from lambda invocation
  - shows JSON delivered to lambda

EventBridge- Create rule... Schedule... cron expression... Target Lambda... EC2 Stop function
  - time in UTC, create rul that runs in a few minutes
  - EC2Stop rule triggers, both EC2 instances stop, EC2Protect rule starts instance 1 again

## Serverless Architecture
The Serverless architecture is a evolution/combination of other popular architectures such as event-driven and microservices.
It aims to use 3rd party services where possible and FAAS products for any on-demand computing needs.
Using a serverless architecture means little to no base costs for an environment - and any cost incurred during operations scale in a way with matches the incoming load.
Serverless starts to feature more and more on the AWS exams - so its a critical architecture to understand.

What is serverless?
- isn't one thing
- You manage few, if any, servers- low overhead
  - start up, do one thing realy well, shut down
- Applications are a collection of small and specialized functions
- ...Stateless and Ephemeral environments- duration billing
- Event-Driven- consumption only when being used
- FaaS is used where possible for compute functionality
  - zero cost until something generates an event
- Managed Services are used where possible

Architecture (assume no servers or EC2 isntances)
- User video -> S3 static site (HTML + JS, JS run in user's browser) 
  - app uses 3rd party identity provider (JS -> Google IDP, receive token)
  - Browser -> Cognito (swap Google token for AWS Temp Credentials)
  - Browser -> Upload video to S3 Bucket (using temp credentials)
  - Upload generates event -> Lambda -> Elastic Transcoder service (job for each size video created) -> each job outputs to S3 Transcode bucket and DynamoDB
  - Client Browser -> Lambda (My Media) -> DnamoDB (returns URLs with videos belonging to client)
- All managed services 
  - simplified here- API gateway would be used between user and Lambda

