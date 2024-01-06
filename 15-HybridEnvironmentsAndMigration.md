# Hybrid Environments and Migration

## Border Gateway Protocol 101 (BONUS content)

Routing protocol,  used by some AWS services such as Direct Connect and Dynamic Site to Site VPNs.

- Autonomous System (AS)- routers controlled by one entity... a network in BGP
  - black boxes that abstract away detial
- ASN are unique and allocated by IANA, typically 16-bit (0-65535, 645122-65534 are private)
- BGP operates over tcp/179- it's reliable
- Not automatic- peering is manually configured
  - each system exchanges network topology info with each other
- BGP is a path-vector protocol, it exchanges the best path to a destination between peers, doesn't accout for link speed or condition, the path is called the ASPATH
- iBGP = Internal BGP- routing withing AS
- eBGP = External BGP- routing between ASs

### BGP Topology

Brisbane (ASN 200) 10.16.0.1/16 <-> Adelaide (ASN 201) 10.17.0.1/16 <-> Alice Springs (ASN 202) 10.18.0.1/16

- Brisbane routes table contains Destination, Next Hop (0.0.0.0. means local), ASPATH (i means this network)
- each peer will excahnge best path to a destination with each other, at first only itself
- Brisbane adds Destination 10.17.0.0/16, Next Hop 10.17.0.1, ASPATH 201,i
  - same for Alice Springs router destination, Brisbane now knows about both other ASs
  - Adelaide in the same way will learn about network in Alice Springs
  - Alice Springs will also learn about Brisbane and Adelaide ASs
  - networks can route traffic to other 2
- Brisbane adds another route for going other direction to Alice Springs 10.17.0.01/16
  - Destination 10.18.0.0/16, Next Hop 10.17.0.1, ASPATH 201,202,i
  - prepend own ASN onto path
- AS advertise shortest route to other systems
- end up with HA network, BGP aware of multiple routes in case one fails
  - longer paths are non-preferred, BGP prefers shortest path
- shortest connection might be slower (e.g. fiber vs satellite), but BGP would use by default
  - AS Path Prepending can be used to artificially make the satellite path look longer making the fiber path preferred
  - ASPATH 202,202,202,i
- BGP networks work together to create a dynamic topology

## IPSec VPN Fundamentals
