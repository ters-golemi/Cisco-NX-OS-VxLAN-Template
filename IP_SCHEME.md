# IP Address and BGP Scheme

## Management Network
| Device   | Management IP    | Description          |
|----------|------------------|----------------------|
| Spine-1  | 192.168.1.1/24   | Out-of-band mgmt     |
| Spine-2  | 192.168.1.2/24   | Out-of-band mgmt     |
| Leaf-1   | 192.168.1.11/24  | Out-of-band mgmt     |
| Leaf-2   | 192.168.1.12/24  | Out-of-band mgmt     |

## Loopback Addresses

### Router IDs (Loopback0)
| Device   | Loopback0       | Purpose                    |
|----------|-----------------|----------------------------|
| Spine-1  | 10.0.0.1/32     | BGP Router ID              |
| Spine-2  | 10.0.0.2/32     | BGP Router ID              |
| Leaf-1   | 10.0.0.11/32    | BGP Router ID              |
| Leaf-2   | 10.0.0.12/32    | BGP Router ID              |

### VTEP Addresses (Loopback1)
| Device   | Loopback1       | Purpose                    |
|----------|-----------------|----------------------------|
| Leaf-1   | 10.0.0.111/32   | NVE/VTEP Source            |
| Leaf-2   | 10.0.0.112/32   | NVE/VTEP Source            |

## Point-to-Point Links (Underlay)

### Spine-1 Links
| Interface      | IP Address    | Connected To        |
|----------------|---------------|---------------------|
| Ethernet1/1    | 10.1.1.0/31   | Leaf-1 e1/1         |
| Ethernet1/2    | 10.1.1.2/31   | Leaf-2 e1/1         |

### Spine-2 Links
| Interface      | IP Address    | Connected To        |
|----------------|---------------|---------------------|
| Ethernet1/1    | 10.1.2.0/31   | Leaf-1 e1/2         |
| Ethernet1/2    | 10.1.2.2/31   | Leaf-2 e1/2         |

### Leaf-1 Links
| Interface      | IP Address    | Connected To        |
|----------------|---------------|---------------------|
| Ethernet1/1    | 10.1.1.1/31   | Spine-1 e1/1        |
| Ethernet1/2    | 10.1.2.1/31   | Spine-2 e1/1        |

### Leaf-2 Links
| Interface      | IP Address    | Connected To        |
|----------------|---------------|---------------------|
| Ethernet1/1    | 10.1.1.3/31   | Spine-1 e1/2        |
| Ethernet1/2    | 10.1.2.3/31   | Spine-2 e1/2        |

## BGP Autonomous Systems

| Device   | BGP AS  | Role                |
|----------|---------|---------------------|
| Spine-1  | 65000   | Route Reflector     |
| Spine-2  | 65000   | Route Reflector     |
| Leaf-1   | 65001   | Client              |
| Leaf-2   | 65002   | Client              |

## VxLAN VNI Assignments

### Layer 2 VNIs (VLAN to VNI Mapping)
| VLAN | VNI   | Description      | Tenant    |
|------|-------|------------------|-----------|
| 10   | 10010 | Web Servers      | Tenant-A  |
| 20   | 10020 | App Servers      | Tenant-A  |
| 30   | 10030 | Web Servers      | Tenant-B  |

### Layer 3 VNIs (VRF to VNI Mapping)
| VRF       | VNI   | VLAN | Description           |
|-----------|-------|------|-----------------------|
| Tenant-A  | 50001 | 999  | L3VNI for Tenant-A    |
| Tenant-B  | 50002 | 998  | L3VNI for Tenant-B    |

## SVI/Gateway Addresses (Anycast Gateway)

### Tenant-A VRF
| VLAN | Subnet          | Gateway IP    | Description  |
|------|-----------------|---------------|--------------|
| 10   | 10.10.10.0/24   | 10.10.10.1    | Web Tier     |
| 20   | 10.10.20.0/24   | 10.10.20.1    | App Tier     |

### Tenant-B VRF
| VLAN | Subnet          | Gateway IP    | Description  |
|------|-----------------|---------------|--------------|
| 30   | 10.20.30.0/24   | 10.20.30.1    | Web Tier     |

## Route Distinguisher & Route Target

### Leaf-1
- RD for VRFs: auto (uses 10.0.0.11:*)
- RT for VRFs: auto

### Leaf-2
- RD for VRFs: auto (uses 10.0.0.12:*)
- RT for VRFs: auto
