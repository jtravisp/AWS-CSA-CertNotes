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

## Simple Notification Service
a PUB SUB style notification system which is used within AWS products and services but can also form an essential part of serverless, event-driven and traditional application architectures.

- Public AWS Service- network connectivity with Public Endpoint
- coordinsates the sending and delivery of messages
- messages are <= 256KB payloads
- SNS Topics are the base entity of SNS- permissions and configuration
- Publishers send messages to TOPICS
- Subscribers receive messages SENT to TOPICS.
  - e.g. http(s), email(JSON), SQS, mobile push, SMS messages, Lambda
- SNS supports a wide variety of subscriber types including other AWS services such as LAMBDA and SQS.

### Architecture
Public Internet <-> Public AWS Zone <-> Private Zone (VPC)

Services from all zones send messages to Topic in Public AWS Zone -> mobile push, SQS queue, Lambda, etc
Fanout- send a single message, fan out to multiple SQS queues

### SNS
- Delivery Status (including http, Lambda, SQS)
- Delivery retries- reliable delivery
- HA and Scalable (Region)
- Server Side Encryption (SSE)
- Cross-account via TOPIC Policy

## Step Functions
build long running serverless workflow based applications within AWS which integrate with many AWS services

Some problems with Lambda
- Lambda is FaaS
- 15 minute max execution time
- can be chained together
- gets messy at scale
- runtime environments are stateless

State Machines
- serverless workflow- Start -> States -> End
- States are THINGS which occur
  - thing placing and order from Amazon, everything that happens behind the scenes to process order
- Max duration 1 year
- Standard Workflow and Express Workflow (standard default)
  - Express for highly transaction, processing guarantees
- Started via API gateway, IOT rules, EventBridge, Lambda...
- Amazon States Language (ASL)- JSON Template
- IAM Role is used for permissions (State machine assumes role)

States
- SUCCEED and FAIL 
- WAIT (waits period of time or until specific date/time), stops workflow
- CHOICE (path based on input, e.g. stock level of items in an order)
- PARALLEL (parallel branches)
- MAP (accepts list of things, e.g. list of orders, perform action for each item)
- TASK (single unit of work performed by state machine- Lambda, Batch, DynamoDB, ECS, SNS, DQD, Glue, SageMaker, EMR, Step Functions)

Step Functions
State Machine : Timer -> Choice (3 paths, notfication type) -> EmailOnly, EmailAndSMS, SMSOnly (invokes required Lambdas)
- Lambdas -> Eimple Email Service (SES) and/or Simple Notification Service (SNS)
- Browser (static website) -> API Gateway -> API_:ambda -> State machine, begins execution

## API Gateway 101
managed service from AWS which allows the creation of API Endpoints, Resources & Methods.
The API gateway integrates with other AWS services - and can even access some without the need for dedicated compute.
It serves as a core component of many serverless architectures using Lambda as event-driven and on-demand backing for methods.
It can also connect to legacy monolithic applications and act as a stable API endpoint during an evolution from a monolith to microservices and potentially through to serverless.

- Create and manage APIs
- Enpoint/entrypoint for applications
- sits between applications and integraitons (services)
- HA, scalable, handles authorization, throttling, caching, CORS, transformation, OpenAPI spec, direct integration
- can connect to services/endpoints in AWS or on-prem
- http APIs, REST APIs, and WebSocket APIs

Overview
- Apps and Services -> API Gateway (endpoint)
  - intermediary between clients and integrations
- 3 Phases
  - Request (authorizes, transforms, and vaildates)
  - Integrations
  - Response (transform, prepare, return)
- API Gateway cache can be used to reduce the number of calls made to abckend integrations and improve client performance
- CloudWatch logs can store and manage full stage request and responce logs. CW can store metrics for client and integration sides

Authentication
- auth not required
- can use Cognito User Pools for suth
  - Cognito -> client (authenticate with Cognito and receive token) -> pass token with request -> API Gateway -> verify token validity
    - API Gateway -> Lambda authorizer called -> call to ID provider or compute based check of ID
    - -> IAM policy and principal identifier

Endpoint Types
- Edge-Optimized
  - routed to the nearest CF POP
- Regional- clients in the same region (low overhead)
- Private- endpoint accessible only within a VPC via interface endpoint

Stages
- APIs are deployed to stages, each stage has one deployment
- client browser -> api.catagram.io/prod
- developers -> api.catagram.io/dev
- Stages can be enabled for canary deployment. If done, deployments are made to the canary, not the stage
- Stages enabled for canary deployments can be configured so a certain percentage of traffic is sent to the canary
  - can be adjusted over time- or the canary can be promoted to make it the new base 'stage' (or removed)

Errors (*memorize these*)
https://docs.aws.amazon.com/apigateway/latest/api/CommonErrors.html
- Two categories:
  - 4XX - Client error- invalid request on client side
    - 400 - Bad Request- Generic
    - 403 - Access Denied- Authorizer denies... WAF filtered
    - 429 - API Gateway can throttle- this means you've exceeded that amount
  - 5XX - Server error- valid request, backend issue
    - 502 - Bad Gateway Exception- bad output returned by lambda
    - 503 - Service Unavailable- backing endpoint offline? Major services issues
    - 504 - Integration Failute/Timeout- 29s limit

Caching
- API GW Stage
- without cache: backend servces used on every request
- with cache: TTL default is 300 s, config min 0 and max 3600
  - backend calls used only on cache miss
  - cache is defined per stage within API GW

## Build a Serverless App - DEMO (52m)
https://github.com/acantril/learn-cantrill-io-labs/tree/master/aws-serverless-pet-cuddle-o-tron
https://github.com/acantril/learn-cantrill-io-labs/blob/master/aws-serverless-pet-cuddle-o-tron/02_LABINSTRUCTIONS/CommonIssues.md

implementing a serverless reminder application.
The application will load from an S3 bucket and run in browser
.. communicating with Lambda and Step functions via an API Gateway Endpoint
Using the application you will be able to configure reminders for 'pet cuddles' to be send using email and SMS.

### Stage 1
Simple Email Service (SES)- starts in sandbox, can remove (takes time) of verify individual addresses
- whitelist address that emails will be coming from
  - Verified identities... email address.... from email address (e.g. travis+cuddleotron@travispollard.com)
- email address that email will be sent TO (e.g. travis+cuddlecustomer@travispollard.com)

### Stage 2
Create IAM role for Lambda function (CF Deployment)
Create email reminder Lambda function (email_reminder_lambda), use Python 3.11
```
import boto3, os, json

FROM_EMAIL_ADDRESS = 'travis+cuddleotron@travispollard.com'

ses = boto3.client('ses')

def lambda_handler(event, context):
    # Print event data to logs .. 
    print("Received event: " + json.dumps(event))
    # Publish message directly to email, provided by EmailOnly or EmailPar TASK
    ses.send_email( Source=FROM_EMAIL_ADDRESS,
        Destination={ 'ToAddresses': [ event['Input']['email'] ] }, 
        Message={ 'Subject': {'Data': 'Whiskers Commands You to attend!'},
            'Body': {'Text': {'Data': event['Input']['message']}}
        }
    )
    return 'Success!'
```
Deploy Lambda function... copy down ARN for function

### Stage 3
Add State Machine, waits certain emaount of time, then uses Lambda function and SES to send an email
Create role
  - 1-click deployment (CF)
  - service: states.amazonaws.com
  - permissions: cloudwatchlogs, invokelambdasandsendSNS
Create state machine
  - Step functions... State machines, Create... Blank... Code...
```
{
  "Comment": "Pet Cuddle-o-Tron - using Lambda for email.",
  "StartAt": "Timer",
  "States": {
    "Timer": {
      "Type": "Wait",
      "SecondsPath": "$.waitSeconds",
      "Next": "Email"
    },
    "Email": {
      "Type" : "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "EMAIL_LAMBDA_ARN",
        "Payload": {
          "Input.$": "$"
        }
      },
      "Next": "NextState"
    },
    "NextState": {
      "Type": "Pass",
      "End": true
    }
  }
}
```
  - Wait state (sedonds received as input), Task state: Invoke Lambda (email, payload is input to state machine), NextState: Pass, true
Integrate with Lambda function
  - Add ARN of Lambda function
  - Config... change name to "PetCuddleOTron"... Standard.... Permissions... choose state machine role created earlier... logging All... Create
  - Dedicated log group will be created... copy down ARN

### Stage 4
Add API Gateway and supporting Lambda function

Lambda... Create... name "api_lambda"... Python 3.11... choose Lambda role... Create
This is the function which will provide compute to API Gateway
```
# This code is a bit ...messy and includes some workarounds
# It functions fine, but needs some cleanup
# Checked the DecimalEncoder and Checks workarounds 20200402 and no progression towards fix

import boto3, json, os, decimal

SM_ARN = 'YOUR_STATEMACHINE_ARN'

sm = boto3.client('stepfunctions')

def lambda_handler(event, context):
    # Print event data to logs .. 
    print("Received event: " + json.dumps(event))

    # Load data coming from APIGateway
    data = json.loads(event['body'])
    data['waitSeconds'] = int(data['waitSeconds'])
    
    # Sanity check that all of the parameters we need have come through from API gateway
    # Mixture of optional and mandatory ones
    checks = []
    checks.append('waitSeconds' in data)
    checks.append(type(data['waitSeconds']) == int)
    checks.append('message' in data)

    # if any checks fail, return error to API Gateway to return to client
    if False in checks:
        response = {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin":"*"},
            "body": json.dumps( { "Status": "Success", "Reason": "Input failed validation" }, cls=DecimalEncoder )
        }
    # If none, start the state machine execution and inform client of 2XX success :)
    else: 
        sm.start_execution( stateMachineArn=SM_ARN, input=json.dumps(data, cls=DecimalEncoder) )
        response = {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin":"*"},
            "body": json.dumps( {"Status": "Success"}, cls=DecimalEncoder )
        }
    return response

# This is a workaround for: http://bugs.python.org/issue16535
# Solution discussed on this thread https://stackoverflow.com/questions/11942364/typeerror-integer-is-not-json-serializable-when-serializing-json-in-python
# https://stackoverflow.com/questions/1960516/python-json-serialize-a-decimal-object
# Credit goes to the group :)
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)
```
Paste in your ARN for the state machine... Deploy

API Gateway service... APIs... REST API... Build... New API... "petcuddleotron"... Regional (scalable and HA)
  - Create resource... "/petcuddleotron"... enable CORS... Create
    - CORS: This relaxes the restrictions on things calling on our API with a different DNS name, it allows the code loaded from the S3 bucket to call the API gateway endpoint
  - Create Method... POST... Lambda function... us-east-1... api...find Lambda function created earlier.... use Default timeout and Lambda proxy integration
  - Deploy API... Create new stage called "prod"... Deploy
  - Copy down Invoke URL... used by client application to conenct to serverless application

### Stage 5
Create S3 bucket
  - S3... Create bucket.... select random unique name... us-east-1... uncheck block public access
  - Bucket permissions... bucket policy... edit
```
{
    "Version":"2012-10-17",
    "Statement":[
      {
        "Sid":"PublicRead",
        "Effect":"Allow",
        "Principal": "*",
        "Action":["s3:GetObject"],
        "Resource":["REPLACEME_PET_CUDDLE_O_TRON_BUCKET_ARN/*"]
      }
    ]
  }
```
  - Use ARN of actual bucket

Configure as static website
  - Proerties of bucket... Static website hsoting... Edit... Enable... Host a static website...index.html... Save
  - Copy down Bucket Website Endpoint URL

Edit client application files to point to serverless application (API Gateway address)
  - Download serverless frontend zip, html, css, png image
  - edit serverless.js, add your API gateway URL
  - Upload files to S# bucket
  - Open bucket URL, site should open
  - Enter time in seconds (try 120) and message and email (can only use verified emails)
  - Check State Machine in AWS...  refresh executions and should see currently running execution
    - part in blue is currently running... green means complete
    - Execution input and output shows parameters passed in to state machine
    - Click logging... see all log items for execution

### Stage 6 
Cleanup
  - Empy bucket, delete bucket
  - Delete API
  - Delete lambda
  - Delete state machine
  - Delete CF stacks

## Simple Queue Service (SQS)
Managed message queue service in AWS which help to decouple application components, allow Asynchronous messaging or the implementation of worker pools

- Public, fully managed, HA queues - Standard or FIFO
  - FIFO guarantees order, Standard is best effort, messages could be received out of order
- Messages up to 256KB in size- link to large data
- Received messages are hidden (VisibilityTimeout- time message hidden unless explicitly deleted)
  - client can delete message, after timeout reappears (retry)
- Dead-letter queue can be used for problem messages, different processing for messages that keep coming back
- ASGs can scale and Lambdas invoke based on queue length

ASG Worker Pool -- ASG Web Pool
- User sends file -> Web Pool, Web Pool creates message and sends file to S3
- Web Pool scaled out when CPU high, scaled in when CPU low
- Worker Pool scaled out when queue length long, scaled in when queue length short
- Queue -> Worker Pool, Worker pool pulls file from S3 -> Transcode bucket
- Auto scaling group always look at queue for scaling
- Web pool pulls from transcode bucket and gives back to user
- Production app would use SNS and SQS Fanout, SNS topic has subscribers, one for each resolution (480p, 720p, 1080p)
  - can independently scale
  - one SNS topic, meassage added to each queue
  - ***EXAM*** remember fanout architecture 

SQS
- Standard (multilane highway)- at least once, FIFO (single lane road)- exactly once
- FIFO Performance- 3,000 messages /s with batching, or up to 300 /s without
- billed based on requests
- 1 request = 1-10 messages up to 64KB total
- Short (immediate) vs Long (waitTimeSeconds) Polling
  - Short will increase billing, Long will wait for messages (up to 20 s), you should use Long polling
- Encryption at rest (KMS) and in-transit
- Queue policy (or identity policy) for access to queue

## SQS Standard vs FIFO Queues
FIFO- Single lane highway
- 300 TPS w/o batching (up to 10 messages), 3,000 with
- Exactly-Once processing, message order is strictly preserved
- need FIFO suffix .fifo

Standard- Multilane highway
- Scalable, as wide as required, near unlimited TPS
- faster, multiple messages carried at same time
- no rigid message ordering, messages could be delivered more than once
- ideal for decoupling, worker pools, batch for future processing

## SQS Delay Queues
 Provide an initial period of invisibility for messages. Predefine periods can ensure that processing of messages doesn't begin until this period has expired.

 Postpone delivery of messages to consumer
 - SQS Queue
   - SendMessage- mesaage added
   - Visibility timeout takes effect
     - ReceiveMessage- No messages
   - DeleteMessage or not
   - Reappear on Queue if not Deleted, allows for reprocessing
 - Delay Queue
   - messages added start in invidible state for DelaySeconds period
   - ReceiveMessages returns No Messages
   - default delay is 0, max 15 minutes
   - not supported on FIFO queues
   - generally used when delay in processing is needed for application

## SQS Dead-Letter Queues
Allow for messages which are causing repeated processing errors to be moved into a dead letter queue
In this queue, different processing methods, diagnostic methods or logging methods can be used to identity message faults

Message (invisible for Visibility Timout), processing fails, message keeps reappearing
- Dead-letter queues- ReceiveCount increments
- redrive policy: specifies Source Queue, the Dead-Letter queue, and the conditions where messages will be moved from on to the other
  - Defince maxReceiveCount
  - when ReceiveCount > maxReceiveCount and message isn't deleted, it's moved to teh dead-letter queue
- timestamp maintained, retention period doesn't change

## Kinesis Data Streams
*often confused with SQS*
Streaming service within AWS designed to ingest large quantities of data and allow access to that data for consumers.
Kinesis is ideal for dashboards and large scale real time analytics needs.
Kinesis data firehose allows the long term persistent storage of kinesis data onto services like S3

- Scalable Streaming service
- Producers send data into a kinesis stream
- Streams can scale from low to near infinite data rates
- Public service and HA by design
- Streams store a 24-hour moving window of data
- ...can be increased to a maximum of 365 days (additional cost)
- Multiple consumers access data from that moving window

Architecture
Producers (EC2, servers, mobiel apps, IOT sensors) -> Kinesis Stream -> Consumers (servers, EC2, Lambda)
  - stream starts with 1 shard, shards added to scale
    - each shard: 1 MB ingestion, 2 MB consumption
    - data stored via Kinesis Data Record (max 1MB)
    - Kinesis Firehose moves data to another service (like S3)

SQS vs Kinesis
- Ingestion of data? - Kinesis, otherwise think SQS first
- SQS 1 production group, 1 consumption group
- SQS Queues - Decoupling and Asynchronous communications
  - No persistence of messages, no window (deleted after processing)
- Kinesis- huge scale ingestion
  - ...multiple consumers... rolling window
  - Data ingestion, Analytics, Monitoring, App Clicks

## Kinesis Data Firehose
Stream based delivery service capable of delivering high throughput streaming data to supported destinations in near realtime.
Its a member of the kinesis family and for the PRO level exam it's critical to have a good understanding of how it functions in isolation and how it integrates with AWS products and services.

- Kinesis doesn't persist data after rolling window
- Firehose- fully managed service to load data for data lakes, data stores, and analytics services
- Automatic scaling... fully serverless... resilient
- Near real time delivery (~60s)
- Supports tranformation of data on the fly (using Lambda)
- Billing- volume through firehose

Architecture
- Kinesis Data Firehose -> HTTP, Splunk, Redshift, ElasticSearch, S# Destination Bucket
- Producers (Cloudwatch Logs and Events, KPL, Kinesis Agents, Internet of Things) -> Kinesis Data Stream -> Kinesis Data Firehose
  - Kinesis streams are realtime ~200ms
  - Producers can also send data directly to Firehose
  - Firehose offers near realtime delivery... delivery when buffer size in MB (1) fills or buffer interval in seconds (60) passes
- Firehose can tranform data with Lambda
  - Firehose -> Lambda Trasformation Function (Blueprints) -> Firehose
  - can also store Source Records in S3 Backup Bucket
  - Devlivery to Redshift uses S3 as an intermediate
    - Firehose -> S3 -> Redshift
- need to be able to pick if Firehose is a valid solution

Uses
- provide persistence to data coming into Kinesis Stream
- Store data in diff format (Lambda)
- Deliver data to supported product (but not real time)

## Kinesis Data Analytics
Easiest way to analyze streaming data, gain actionable insights, and respond to your business and customer needs in real time.
It is part of the kinesis family of products and is capable of operating in realtime on high throughput streaming data.

Firehose- delivery service (and transformation with Lambda)
Kinesis Data Analytics- real time processing of data
  - uses Structured Query Language (SQL)
  - ingests from Kinesis Data Streams or Firehose
  - Destinations
    - Firehose (S3, Redshift, ElasticSearch, Splunk)
    - AWS Lambda
    - Kinesis Data Streams

Source Stream (Kinesis Stream/Kinesis Firehose) -> Kinesis Analytics App -> Destination Stream (Kinesis Stream/Kinesis Firehose)
  - Refernce Data (S3 Bucket)
  - Kinesis Analytics App- In-application input stream and Static data used to enrich the streaming input (S3)
    - Application Code processes input and produces output (SQL) -> In-application output streams -> Destination Stream
    - SQL -> Errors generated from processing (In-aplication error stream)
  - only pay for data processed by application

When and Where
- Streaming data needing real-time SQL processing
- Time-serice analytics- elections, e-sports
- Real-time dashboards- leaderboards for games
- Real-time metrics- security & response teams

## Kinesis Video Streams
Makes it easy to securely stream video from connected devices to AWS for analytics, machine learning (ML), playback, and other processing.
Kinesis Video Streams automatically provisions and elastically scales all the infrastructure needed to ingest streaming video data from millions of devices.

- Ingest live video data for producers
- Security cameras, smartphones, cars, drones, time-serialized audio, thermal, depth, and radar data
- Consumers can access data frame-by-frams... or as needed
- Can persist and excrypt (in-transit and at rest) data...
- ...can't access directly via storage... only via APIs
- Integrates with other AWS services e.g. Rekognition and Connect

Home Security Camera -> Kinesis Video Streams (1 per camera) -> Rekognition Video (facial recognition) <- Face Collection
  - Rekognition outputs analysis to Kinesis Data Stream -> IDs matched faces -> Lambda function analyzes every record -> SNS -> email notification

## Amazon Cognito - User and Identity Pools
A user pool is a user directory in Amazon Cognito. With a user pool, your users can sign in to your web or mobile app through Amazon Cognito.
Your users can also sign in through social identity providers like Google, Facebook, Amazon, or Apple, and through SAML identity providers. 
Whether your users sign in directly or through a third party, all members of the user pool have a directory profile that you can access through a Software Development Kit (SDK).
Amazon Cognito identity pools (federated identities) enable you to create unique identities for your users and federate them with identity providers. 
With an identity pool, you can obtain temporary, limited-privilege AWS credentials to access other AWS services. 

- Cognito has terrible naming...
- Authentication, Authorization, and User Management for web/mobile apps
- Two Parts: 
  - User Pools (login and managing identities)
    - Sign in and get a JSON Web Token (JWT)
    - User directory management and profiles, sign-up and sign-in (customizable web UI), MFA and other security features
    - can't be used to directly access AWS resources
  - Identity Pools (swap identity for AWS credentials)
    - allows you to offer access to Temporary AWS Credentials
    - Unauthenticated Identities- Guest users (maybe high score stored in DynamoDB)
    - Federated Identities- SWAP- Google FB, Twitter, SAML2., and User Pool for short term AWS Credentials to access AWS Resources
    - assumes IAM role on behalf of identity

User Pools Architecture
- Pool that includes FB, Google, etc -> token (JWT) Authenticate to browser
  - User Pool Token used as proof of auth -> JWT can be used to access self-managed server based resources
  - User Pool Token used as proof of auth -> API Gateway -> Lambda, User Pool tokens can grant access to APIs via Legacy Lambda Custom Authorizers and now directly via API Gateway

Identity Pools Architecture
- External Identities (Google, FB, etc) -> Auth to 3rd party IDP directly and get a token -> Token to user/browser
  - Pass token -> Identity Pool
    - Cognito assumes IAM role defined in Identity Pool and returns temp AWS creds - Authenticated Role and Unauthenticated Role
    - Cognito passes temp AWS creds back to application
    - Application using temp creds -> AWS Services

Can use User Pools and Identity Pools together
- User pools can be used to handle many external identities, ID Pools to swap for AWS creds (Web Identity Federation)
- Coginto User Pool (FB< Google, etc) -> Authenticate (JWT) -> User Pool Token -> Identity Pool
- By using user pools and social sign-in you app can standardize on a single "token" (User Pool Tokens)
- ID Pools swap tokens for AWS auth (Federation)
- Allows for near unlimited number of users

## AWS Glue 101
Fully managed *extract, transform, and load (ETL)* service that makes it easy for customers to prepare and load their data for analytics. 
You can create and run an ETL job with a few clicks in the AWS Management Console. You simply point AWS Glue to your data stored on AWS, and AWS Glue discovers your data and stores the associated metadata (e.g. table definition and schema) in the AWS Glue Data Catalog. 
Once cataloged, your data is immediately searchable, queryable, and available for ETL.

- ...vs datapipeline (which can do ETL) and uses servers (EMR)
- Moves and transforms data between source and destination
- Crawls data sources and generates the AWS Glue Data catalog
- Data Source: Stores: S3, RDS, JDBC Compatible and DynamoDB
- Data Source: Streams: Kinesis Data Stream and Apache Kafka
- Data Targets: S3, RDS, JDBS Databases

Data Catalog- collection of metadata combined with data management and search tools
- Persistent metadata about data sources in region
- One catalog per region per account
- Avoids data silos, improves data visibility across org
- Amazon Athena, Redshift Spectrum, EMR and AWS Lake Formation all use Data Catalog
- ...configure *crawlers* for data sources

Data Sources(S3, RDS, JDBC, Kinesis, etc) -> Crawlers -> Data Catalog
  - Crawlers connect to data stores, determine schema and create metadata in the data catalog
  - Management console access to Data Catalog and job control
  - Data Source -> Data extract -> Glue Job connects to Data Catalog and Data Load -> Supported data targets include S#, RDS, and JDBC compatible databses
  - When resources are required, glue allocates from a AWS Warm Pool to perform the ETL processes

Exam: Data Pipelin OR Glue (keywords: serverless, ad hoc, cost effective)

## Amazon MQ 101
AWS implementation of Apache ActiveMQ
It supports open standards such as JMS, AMQP, MQTT, OpenWire and STOMP
If you need to support any of these, and use queues and topics - AmazonMQ is the tool to use.

- SNS and SQS are AWS Services- using AWS APIs
- SNS provides TOPICS and SQS provides QUEUES
- Public services... highly scalable... AWS integrated
- larger orgs might already use topics and quques... might want to migrate into AWS
- ...SNS and SQS won't work out of the box

MQ
- open-source message broker
- based on managed Apache ActiveMQ
- ...JMS API... protocols such as AMQP, MQTT, OpenWire, and STOMP
- provides Queues and Topics
- One-to-one or ONe-to-Many
- Single INstance (Test, Dev, Cheap) or HA Pait (Active/Standby)
- VPC based- NOT a public service- private networking required
- No AWS native integration... delivers ActiveMQ product which you manage

On-prem message producer interacting with on-prem ActiveMQ -> Direct Connect of Site-to-Site VPN -> Amazon MQ Broker with EFS for shared storage (2 AZs with data replication)
- NOT a public service!

Exam Considerations
- SNS or SQS for most new implementations (default)
- SNS or SQS if AWS integration is required (logging, permissions, encryption, service integration)
- AmazonMQ if APIs such as JMS or protocols such as AMPQ, MQTT, OpenWire, and STOMP are needed
- Remember you need private networking for Amazon MQ

## Amazon AppFlow
Fully managed integration service that enables you to securely transfer data between Software-as-a-Service (SaaS) applications like Salesforce, SAP, Zendesk, Slack, and ServiceNow, and AWS services like Amazon S3 and Amazon Redshift, in just a few clicks. 
With AppFlow, you can run data flows at enterprise scale at the frequency you choose - on a schedule, in response to a business event, or on demand. 
You can configure data transformation capabilities like filtering and validation to generate rich, ready-to-use data as part of the flow itself, without additional steps. 
AppFlow automatically encrypts data in motion, and allows users to restrict data from flowing over the public Internet for SaaS applications that are integrated with AWS PrivateLink, reducing exposure to security threats.

- Fully managed Integration service
- Exchange data between apps (connectors) using *flows*
- Sync data across apps
- Aggregate data from diff sources
- Public endpoints, but works with PrivateLink (privacy)
- AppFlow Custom Connector SDK (build your own)
- e.g. Contact records from SalesForce -> RedShift
- e.g. Support Tickets from ZenDesk -> S3

Flow: Source Connection -> Destination Connection
- Connections store configuration and credentials to access applications
- COnnections can be reused across many flows- they are defined separately
- Configure Source to Destination mapping
- Optional Data Transformation
- Optional Configure filters and validation
