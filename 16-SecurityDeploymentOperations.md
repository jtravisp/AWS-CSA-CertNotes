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

## CloudHSM

## AWS Config

## Amazon Macie

## Amazon Macie DEMO

## Amazon Inspector

## Amazon Guardduty

