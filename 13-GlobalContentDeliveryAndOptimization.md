# Global Content Delivery And Optimization

## Cloudfront Architecture
Content Delivery network (CDN) within AWS

Terms
- Origin- source location of your content
  - S3 Origin or Custom Origin
- Distribution- the "configuration" unit of CloudFront
- Edge Location- local cache of your data (over 200 locations)
- Regional Edge Cache- larger version of an edge location, provides another layer of caching

Upload original content, Configure Distribution, Content -> Distribution
- distribution always ends in cloudfront.net -> custom domain name
- Distribution -> Regional Edge Cache -> Edge Locations
- Regional users are directed to closest edge location
  - if object locally cached, returned immediately (a "cache hit")
  - not stored locally, a "cache miss", edge location might check Regional Edge Cache
    - no hit? Origin Fetch to Regional Cache, then passed to edge location
  - another user gets a cache miss at a differnt edge location, object is now stored in regional cache and returned from there (not origin again)
- Integrates with AWS Cert Manager (ACM) for HTTPS
- Upload direct to origins

"Behavior" is config contained within Distribution
Origins are used by behaviors as content sources
- All start with default (*) behavior
- Origin -> Cache Behavior -> Edge Locations -> User
- e.g. private (img/*)
  - A distribution can have many behaviors which are configured with a path apttern, if requests match that pattern that behavior is used... otherwise default
  - Origins, Origin Groups, TTL, Protocol Policies, restricted access are configured via Behaviors

## Cloudfront (CF)- Behaviors
Control much of the TTL, protocol and privacy settings within CloudFront
Within settings for a CF distribution:
- Price class- where deployed (all, only NA/Europe, NA/Europe/Asia/ME/Africa)
- AWS Web Application Firewall web ACL- optional
- configure alternate domain name
- can choose type of SSL cert (more recent policy could cut out older browsers)
- Behaviors- can configure multiple
  - Default(*)- * matches anything not matches by another more specific behavior
  - HTTP v HTTPS
  - allowed HTTP methods- GET, HEAD, PUT, POST, etc
  - Cache policy
  - Restrict viewer access- must set Trusted authorization type- Trusted key groups or Trusted signer
    - control access to sensitive content
- Know which options set per behavior basis vs distribution
  - all caching controls and viewer access set with behaviors

## Cloudfront- TTL and Invalidations
S3 Origin -> Edge Location -> Users
- photo uploaded to S3, request for photo made, not on edge location, so "origin fetch"
- photo replaced on S3, next request returns old edge location version
- object expires, next request forwards to origin
  - current- 304 Not Modified returned, edge location becomes current again
  - origin has newer- 200 OK returned along with new version of object

Object Validity
- not expired if within TTL period
- More frequent cache HITS = lower origin load
- Default TTL (defined by "behavior") = 24 hours (validity period)
- can set Minimum TTL and Maximum TTL values, can define per object
- Origin Header: Cache-Control max-age (seconds)
- Origin Header: Cache-Control s-maxage (seconds)
  - both direct CF to apply TTL time to an object
- Origin Header: Expires (Date and Time)- when object should expire
- Default TTL is 24 hours, can change per object
- Custom Origin or S3 (via object metadata)

Cache Invalidations
- performed on a distribution
- ...applies to all edge locations... takes time
- define which objects to invalidate
  - /images/whiskers1.jpg
  - /images/whiskers*
  - /images/*
  - /*
- Versioned file names... whickers1_v1.jpg -> v2 -> v3, update app to point to newer version
  - avoids need to invalidate, cached data won't be used
  - logging more effective, know exactly what object used
  - not the same as S3 object versioning

## AWS Certificate Manager (ACM)
Service which allows the creation, management and renewal of certificates. It allows deployment of certificates onto supported AWS services such as CloudFront and ALB.

- HTTP - simple and insecure
- HTTPS - SSL/TLS layer of encryption added to HTTP
- Data is encrypted in-transit
- Certificates prove identity
- Chain of trust- signed by a trusted authority
- ACM lets you run a public or private Certificate Authority (CA)
- Private CA- Applications need to trust your private CA
- Public CA- Browsers trust a list of providers, which can trust other providers

- ACM can generate or import certificates
- If generated... it can automatically renew
- If imported... you are responsible for renewal
- Certs can be deployed out to supported services
- Supported AWS Services ONLY (e.g. CloudFront and ALBs.... NOT EC2)
  
- ACM is a regional service
- Certs cannot leave the region they are generated or imported in
- To use a cert with an ALB in ap-southeast-2 you need a cert in ACM in ap-southeast-2
- Global services such as CloudFront operate as though withing 'us-east-1'
  - Certs created in any other region can't be used with CF

3 Regions: ACM, ALB, EC2 instances -> CF Distro, Edge Locations, S3 Bucket -> Users
- Gen a cert in ACM once per region, ACM -> services in that region (can't deply ACM cross-region, nor to unspuported services like EC2)
- then cert deployed to edge locations
- S3 does not use ACM 

## Cloudfront and SSL/TLS
- CloudFront Default Domain Name (CNAME)
- looks like https://d11111abchhed.cloudfront.net/
- SSL supported by default.... *.cloudfront.net cert
- Alternate Domain Names (CNAMES) e.g. cdn.catagram....
  - point to CF with DNS provider like Route53
- Add SSL cert that matches CF distribution alternate name
- Generate or import a cert in ACM... in us-east-1
  - CF is a global service, so cert must ALWAYS be created in us-east-1
- HTTP or HTTPS, HTTP -> HTTPS, HTTPS only
  - HTTPS- must have appropriate certs that match name
- Two SSL Connections: Viewer -> CF and CF -> Origin
  - BOTH connections need valid public certs and any intermediate certs
  - self-signed certs will NOT work

Cloudfront and SNI
- Historically (before 2003)... every SSL enabled site needed its own IP
- Encryption starts at the TCP connection...
- Host headers happen after that - Layer 7/Application
- Historically web servers could only handle 1 cert, diff sites needed diff IPs
- SNI is a TLS extension, allowing host to be included in TLS handshake
  - server responds with cert for site requested, one IP can host many websites
- Old browsers don't support SNI... CF charges extra for dedicated IP ($600/mo/distribution)

Architecture
Origins (S3, ALB, Custom Origin EC2 or On-Prem) -> Edge Location -> Customers
- Old Browsers: Dedicated IP at each CF Edge Location to support NON SNI capable browsers
- Cert issued by a trusted CA such as Comodo, DigiCert, or Symantex, or ACM (us-east-1) MATCHES THE DNS NAME
  - no self-signed certs!
- Origin <-> Edge Location - Origin Protocol
  - also no self-signed certs
  - S3 origins handle certs natively
  - ALB needs publically trusted cert (external or ACM)
  - Custom- publically trusted cert, but ACM not an option, apply manually
  - Cert must match DNS name of origin!

## CloudFront - Origin Types and Origin Architecture
CloudFront service in web UI...
Open Distribution... Origins...
- Origin Groups allow resiliency, group origins together
  - Origins are selected by "Behaviors"
  - e.g. Default(*) -> Origin or Origin Group
- Origin: S3, MediaStore, or Everything Else (Custom Origin, i.e. web server)
  - S3 is simplest, designed to work with CF
  - S3 allows for advanced features not avialable with custom origin
    - Legacy access identities- Origin access identity
    - Origin access control settings (recommended)
    - can restrict S3 origin so only accesible from CF distribution
    - same viewer side and origin side protocols
    - can pass through origin custom headers
  - Custom Origin
    - can specifiy path (same as S3 origin)
    - can be more granular with config
    - Minumum origin SSL protocol- best is to select most recent
    - Can pick http(s) port
    - can still pass through custom headers
      - config custom origin to only accept connections from CF

## CloudFront - Adding a CDN to a static website - DEMO
CloudFormation- 1-click deployment, creates static website

S3 Bucket- top20cats has static website
Problems:
  - Users not in us-east-1 region have performance issues
  - Can't deliver with https (S3 can't deliver with https)

CloudFront Service, Create distribution
- Origin domain, select website bucket
  - Pick S3 bucket- will use S3 origin, Pick DNS name- will use custom origin
    - S3 origin gives additional functionality
- Origin path is optional, default select root
- Origin can still be accessed directly (not ideal)
- Viewer- HTTP and HTTPS, redirect HTTP to HTTPS, or HTTPS only
- Cache key and origin request
  - Legacy settings is the old way
  - New is "Cache policy and origin request policy"- groupings of settings
    - e.g. Managed-CachingOptimized
    - Choose "CachingOptimized" (recommended for S3 origins)
- Real-time logs to Kinesis data stream
- Price class- which edge locations used, default is All (most expensive), can limit to smaller geographical area
- AWS WAF web ACL optional, what gets filtered
- by default given domain name with SSL cert (*.cloudfront.net)
  - to use own domain name: Alternate domain name (CNAME), point domain name to CF distro, request cert using ACM
- Default root object- index.html (browse to default name without specifying)
- Create distribution

After distribution is "Deployed":
- Note distribution domain name, site will now be delivered from closest edge location
- Upload new version of merlin.jpg image to bucket/img, will overwrite image in the bucket with the same name
- Reload page, doesn't show update image, link directly to S3 will load new image (going directly to origin)
  - image is cached at edge location until TTL reached
- To update objects:
  - add version to files name, e.g. merlinv2.jpg
  - Perform invalidation, go to CF distribution, invalidations tab, Create invalidation, select object paths (e.g. /img/* for all images, /* for everything)
    - has to go to every edge location, so can take some time
  - might still see incorrect image if it's locally cached (try in private window)
  - billed per invalidation, so better to do bigger less frequently

- With CloudFront, can now use https

## CloudFront (CF)- Adding an Alternate CNAME and SSL

