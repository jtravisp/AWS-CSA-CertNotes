# S3

## S3 Security (Resource Policies and ACLs)
S3 is private by default
    - only identity with initial access is account root user, all other permissions explicitly granted
  
S3 Bucket Policy
    - resource policy
      - like identity policy, but attached to bucket
      - can allow access from other accounts
      - allow/deny anonymous principals
 Bucket: secretcatproject
    - attached: Bucket Policy
    `"Principal": "*",`
        - defines who statement applies to, not in identity policy (because it by definition applies to that user)
        - * means policy applies to anyone accessing bucket, can perform defined action
        - can only have one bucket policy, with many statements

Access Control Lists (ACLs)- on objects or buckets
    - Subresource
    - Legacy (use policies instead)
    - Inflexible, simple permissions

Block Public Access
    - Resource Permissions- public could access bucket with no restrictions if turned on
    - AWS added Block public access settings
    - Failsafe

### Which policy?
Identity: controlling diff. resources
Identity: you have a preference for IAM
Identity: same account
Bucket: just controlling S3
Bucket: anonymous or cross-account
ACLs: never- unless you must

## S3 Static Hosting
Accessing S3 is generally done via APIs
- secure, flexible

Static website hsoting- access via HTTP
Enable
- set Index (what you get when you don't specify a page) and Error documents
- Website Endpoint created (name influenced by bucket name and endpoit, auto generate)
    - can only use custom domain name IF bucket name matches domain name

Scenarios
- Offloading
  - e.g. top10.animals4life.org
  - dynamic (needs DB)?- not suitable for S3
  - static media? perfect!
  - move media/images to S3 with static hosting enabled
  - much cheaper than storing in compute service
- Out-of-band pages
  - e.g. show maintenance page from separate server
  - another service, change DNS and point customers to nackup site on S3

Pricing
- cost to store, per GB/month
- data transfer
  - data in always free
  - data out, per GB
- requesting data (every GET, LIST, PUT, etc)
  - cost per 1,000 operations
  - if use is heavy might use lots of requests
- Free
  - 5GB storage monthly
  - 20k GET and 20K PUT requests

## S3 Static Site Demo


