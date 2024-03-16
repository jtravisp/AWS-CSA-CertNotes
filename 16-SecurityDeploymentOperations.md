# Security, Deployment, and Operations

## AWS Secrets Manager
AWS Secrets manager is a product which can manage secrets within AWS. There is some overlap between it and the SSM Parameter Store - but Secrets manager is specialised for secrets.

Additionally Secrets managed is capable of automatic credential rotation using Lambda.

For supported services it can even adjust the credentials of the service itself.

AWS Secrets Manager vs Paramter Store
- shares functionality
- SM designed for secrets (passwords, API keys)
- usable via console, CLI, API, or SDKs (integration)
- supports automatic rotation... uses Lambda
- directly integrates with some AWS products (RDS)
  - rotating secrets? RDS? Pick Secrets Manager
- can us IAM permissions to control access

Architecture
- "Catagram" app <-> RDS
  - Catagram App to retrieve DB creds <-> SDK <-> IAM
    - SDK <-> SM
  - SM <-> Lambda (permissions via IAM roles)
    - Lambda is invoked preiodically to rotate secrets- products such as RDS are kept in sync
- secured with KMS
- RDS or secrets? Use SM!

## Application Layer (L7) Firewall
Application Layer, known as Layer 7 or L7 firewalls are capable of inspecting, filtering and even adjusting data up to Layer 7 of the OSI model. They have visibility of the data inside a L7 connection. For HTTP this means content, headers, DNS names .. for SMTP this would mean visibility of email metadata and for plaintext emails the contents.

Normal Firewalls
- Layer 3/4
  - Packets, segments, IP addresses, ports
  - Sees requests from laptop -> server and responses server -> laptop
- Layer 5
  - add Session capability Request and Response can be considered part of one session
    - reduces admin overhead and allow for more Contextual security
- Neither understand data on top (like HTTP), Layer 7 is opaque

Layer 7 Firewall
- Client -> L7 FW -> Server
  - FW can understand lower levels + addtl. capabilities
  - HTTP is L7
  - can ID normal or abnormal elements
  - Encryption (HTTPS) terminated (decrypted) on the L7 FW
  - NEW encrypted L7 connection between FW and backend
  - data can be inspected and blocked, replaced or tagged (adult, spam, off-topic, etc)
  - can be granular in how content is handled, block specific apps, services
- keeps L 3/4/5 features

## Web Application Firewall (WAF), WEBACLs, Rule Groups, and Rules

AWS WAF is a web application firewall that helps protect your web applications or APIs against common web exploits and bots that may affect availability, compromise security, or consume excessive resources.

- AWS implementation of L7 FW
- WAF Architecture (can be simple or complex)
  - WAF supports CF, ALB, AppSynv, API GW
    - config is WEB ACL associated with CF distribution, CF is protected by WAF
    - configure when you create the WEB ACL
      - Rule Groups with Rules, Rule Groups within WEBACL
        - Allow list, Deny list, SQL injection, XSS, HTTP flood, IP Reputation, Bots, etc
      - update WEBACLs manually or based on rules
    - WAF outputs logs -> S3 (5min) -> CW Logs -> Firehose -> S3
    - Lambda event driven processing of logs or event subscriptions
    - Take basic WAF and create feedback loop to take data and ID actionable intelligence

WEBACL
- controls if traffic is allowed or blocked
- WEBACL Default Action (ALLOW or BLOCK) - non matching
- Resource Type- CloudFront or Regional Service
- ...ALB, API GW, AppSync... Pick Region
- Add rule groups or rules... processed in order
  - Rules have compute requirement based on complexity, there is a limit
- WEBACL Capacity Units (WCU)- default 1500 WCU... can be incresed with support ticket
- WEBACLs are associated with resources (this can take time), adjusting takes less time than creating new

Rule Groups
- Rule Groups contain Rules
- don't have default actions... that's defined when groups or rules are added to WEBACLs
- Managed (AWS or Marketplace), Yours, Service Owned (i.e. Shield and FW Manager)
- Rule groups can be referenced by multiple WEBACL
- Have a WCU capacity (defined upfront, max 1500)

WAF Rules
- Type, Statement, Action
- Type: Regular (e.g. mattch if something occurs, like SSH from certain IP) or Rate-Based (e.g. rate something occurs, like SSH connections per minute)
- Statement: (WHAT to match) or (COUNT ALL) or (WHAT & COUNT)
  - ...origin country, IP, label, header, cookies, query parameter, URI path, query string, body (first 8192 bytes only), HTTP method
  - Single, AND, OR, NOT
- Action: Allow, Block, Count, Captcha... Custom response (x-amzn-waf-), Label
  - Allow is not valid for rate-based rules, rate-based only have Block, Count, Captcha
  - Labels are internal to WAF, another rule can be based on label presence, can be referenced in the same WEBACL
  - ALLOW and BLOCK stop processing, Count/Captcha actions continue

Pricing
- WEBACL- monthly ($5/month, might change)- can be reused across products
- Rule on WEBACL- Monthly ($1/month)
- Requests per WEBACL- Monthly ($0.60/1 million)
- Intelligent Threat Mitigation
- Bot Control- ($10/month) & ($1 /1 mil requests)
- Captcha- ($0.40 /1K challenge attempts)
- Fraud Control/Account Takeover ($10/month & $ /1K login attempts
- Marketplace Rule Groups- extra costs)

## AWS Shield
AWS Shield is a managed Distributed Denial of Service (DDoS) protection service that safeguards applications running on AWS. AWS Shield provides always-on detection and automatic inline mitigations that minimize application downtime and latency, so there is no need to engage AWS Support to benefit from DDoS protection. 

- Shield Standard and Advanced
  - Standard is free, Advanced has a cost
- 3 types/layers od DDoS attacks
  - Network volumetric attacks (L3) - Saturate capacity
  - Network protocol attacks (L4) - TCP SYN Flood
    - ...leave connections open
    - ...L4 can also have volumetric component
  - Appliation layer attacks (L7) - web flood requests
    - ...query.php?search=all_the_cat_images_ever (essentially use the web app as intended)

- Shield Standard
  - free for AWS customers
  - Protection at the permimeter
  - Region/VPC or the AWS edge
  - Common network (L3) or Transport (L4) layer attacks
  - Best protection using R53, CloudFront, AWS Global Accelerator
- Shield Advanced
  - commercial product, $3,000/month/org, 1 year lock-in + data (OUT) /m
  - protects CF, R53, Global Accelerator, Anything accociated with EIPs (e.g. EC2), ALBs, CLBs, NLBs
  - Not automatic- must be explicitly enabled in Shield Advanced or AWS Firewall Manager Shield Advanced policy
  - Cost protection (e.g. EC2 scaling) for unmitigated attacks
  - Proactive engagement and AWS Shield Response Team (SRT)

Shield Advanced Features
- WAF integration- includes basic AWS WAF fees for web ACLs, rules, and web requests
- Application layer (L7) DDoS Protection (uses WAF)
- Realtime visibility of DDoS events and attacks
- Health-based detection - application specific health checks,  used by Proactive Engagement Team
- Protection groups (reduces admin overhead)

## CloudHSM

CloudHSM - an AWS provided Hardware Security Module products.

CloudHSM is required to achieve compliance with certain security standards such as FIPS 140-2 Level 3

Often cmpared with KMS
- KMS - Key Management Serice in AWS, used for encryption, integrates with other AWS products
  - Shared service (security concern, other accounts can use)
  - uses HSM - Hardware Security Module
- ***CloudHSM is true "single tenant" HSM
- AWS provisioned... fully customer managed (tamper resistent), AWS can't recover this data
- ***FIPS 140-2 Level 3 Compliant
  - KMS is Level 2 compliant overall, some L3
  - need Level 3? Use CloudHSM
- ***CloudHSM is accesed with industry standard APIs
  - PKCS#11, Java Cryptography Extension (JCE), Microsoft CryptoNG (CNG) libraries
- KMS can use CloudHSMas a custom key store, CloudHSM integration with KMS

Architecture
- Customer managed VPC - AWS CloudHSM VPC
  - 2 subnets (AZ-A and AZ-B)
  - in AWS VPC: 1 HSM in each subnet ( 1 in each AZ)
    - cluster across subnets, managed by default by appliances themselves
  - HSMs keep keys and policies in sync when nodes are added or removed
- In customer managed VPC:
  - EC2 instance with AWS CloudHSM Client -> APIs (see above) -> ENI -> HSM (AWS VPC)
- AWS provision HSM but have NO ACCESS to secure area where key material is held

Use Cases
- No native integration between CloudHSM and other AWS products
  - e.g. no S3 SSE
  - could use for client side encryption before uploading to S3
- Offload the SSL/TLS processing from web servers
- Enable transparent data encryption (TDE) for Oracle databases
- Protect private keys for an issuing certificate authority (ICA)
- ***FIPS Level 3? Cloud HSM
- ***AWS integration? KMS

## AWS Config

AWS Config is a service which records the configuration of resources over time (configuration items) into configuration histories.

All the information is stored regionally in an S3 config bucket.

AWS Config is capable of checking for compliance .. and generating notifications and events based on compliance.

Two main jobs
- Record configuration cahnges over time
  - every change creates a configuration item
  - track pre-change state, post-change state, and who changed it
- good for checking for compliance and auditing changes
- does not prevent changes from happening
- Regional service, supports cross-region and account aggregation
- Changes can generate SNS notifications and near realtime events via EventBridge and Lambda

Standard Parts
- Account Resources -> AWS Config -> Config Bucket
- once enabled config of all supported resources is constantly tracked
- every time a change occurs a Configuration Item (CI) is created

Config Rules

- AWS <-> Config Rules
- Resoruces are evaluated against Config Rules- AWS managed or custom (using Lambda)
  - Compliant or Non-Compliant
- AWS Config Rule Changes -> EventBridge -> Remediation (Lambda)
- AWS Config -> ConfigurationStream/ComplianceNotifications

## Amazon Macie

Amazon Macie is a fully managed data security and data privacy service that uses machine learning and pattern matching to discover and protect your sensitive data in AWS.

- Data Security and Data Privacy service
- Discover, Monitor, and Protect Data stored in S3
- Automated discovery of data, e.g. PII, PHI, Finance
- Managed Data Identifiers- Built-in, ML/Patterns
- Custom Data Identifiers - prorietary- Regex based, specific to your business
- Create Discovery Jobs to find data
- Integrates with Security Hub 
- Multi-account architecture, centrally manage either via AWS Org or one Macie account Inviting

Architecture
- Start with 1+ S3 buckets + Macie service
- S3 -> Macie -> Discovery Job (uses managed and custom data identifiers), on a schedule
- Job outputs Findings
- Finding Event -> Event Bridge -> Lambda (maybe automatic fix based on findings)

Macie Identifiers
- Managed data identifiers- managed by AWS
- ...growing list of sensitive data types (credentials, cerdit card, bank, health, etc)
- Custom data identifiers (regex), e.g. `[A-Z]-\d{8}`
- Keywords- optional sequences that need to be in proximity to regex match
- Maximum match distance- how close keywords are to regex patter
- Ignore words- if regex match contains ignore words, it's ignored

Macie Findings
- Policy Findings or Sensitive Data Findings
- Policy- change made after Macie enabled
- Sensitive Data- data in S3 objects based on jobs and identifiers
- Policy e.g. bucket is public, not encrypted, shared externalls, etc
- Sensitive Data e.g. S3 credentials exposed, Financial data, Personally identifiable info

## Amazon Macie DEMO

Go to Macie console and enable
Create job for S3 bucket- check box, Create Job, scheduled or one-time
Manage data identifier options, select all, no allow lists, Submit
  - takes up to 20 minutes to create
Show results.... show findings... to see data identified by Macie

AWS SNS- creat topic for Macie Alerts, confgiure as publisher and subscriber using AWS account number
Create email subscription 

Use Eventbridge to setup notification of Macie findings
Create rule Macie-Events, rule with event pattern
  - Use pattern form, AWS services, Macie, Macie finding
  - Traget SNS topic create above, Create rule

Macie- add custom identifier
  - License Plates, use regex
    - `([0-9][a-zA-Z][a-zA-Z]-?[0-9][a-zA-Z][a-zA-Z])|([a-zA-Z][a-zA-Z][a-zA-Z]-?[0-9][0-9][0-9])|([a-zA-Z][a-zA-Z]-?[0-9][0-9]-?[a-zA-Z][a-zA-Z])|([0-9][0-9][0-9]-?[a-zA-Z][a-zA-Z][a-zA-Z])|([0-9][0-9][0-9]-?[0-9][a-zA-Z][a-zA-Z])`
  - Create license plate job in Macie
Macie should now ID findings on plates data

## Amazon Inspector

Amazon Inspector is an automated security assessment service that helps improve the security and compliance of applications deployed on AWS. Amazon Inspector automatically assesses applications for exposure, vulnerabilities, and deviations from best practices

- Scans EC2 instances and the instance OS for deviations from best practice
- ...also containers
- Vulnerabilities and deviations against best practices
- Provides a report of findings ordered by priority
- Network assessment (agentless)
- Network and host assessment (requires agent)

- Rules packages determine what is checked
- Network reachability (no agent)
- ...Agent can provide additional OS visibility
- Check reachability end to end: EC2, ALB, DX, ELB, ENI, etc
- Returns: RecognizedPortWithListener, RecognizedPortNoListener, RecognizedPortNoAgent
- UnrecognizedPortWithListener

- Packages (...Host assessment, agent required)
- Common Vulnerabilities and Exposures (CVE)
  - CVE on exam? Think Amazon Inspector
- Center for Internet Security (CIS) Benchmarks - EXAM
- Security best practices for Amazon Inspector
  - e.g. disbale root over SSH, modern SSH versions, PW complexity checks, folder permissions

## Amazon Guardduty

Guard Duty is an automatic threat detection service which reviews data from supported services and attempts to identify any events outside of the 'norm' for a given AWS account or Accounts.

Security service, Continuous Security Monitoring Service, runs all the time
- integrated with support data sources, constantly reviewing, uses AI/ML plus threat intelligence feeds
- Identifies unexpected and unauthorized activity on account
- Influence by whitelisting IPs
- on the whole learns what is normal in account
- Notify or event driven protection/remediation based on "Finding"
- Supports multiple accounts (Master and Member accounts)
  
Architecture
- e.g. DNS logs from R53, VPC Flow Logs, CloudTrail event logs, CloudTrail management events, CloudTrail S3 Data events
- ALL -> GuardDuty -> Findings -> CloudWatch EventBridge 
  - Notification -> SNS
  - Invocation -> Lambda
