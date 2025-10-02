# VxLAN/EVPN Deployment Guide

## Prerequisites

### Software Requirements
- Python 3.6 or higher
- pip (Python package manager)
- SSH access to Cisco Nexus switches

### Network Requirements
- Management network connectivity to all switches
- Switches must be reachable at their management IP addresses:
  - Spine-1: 192.168.1.1
  - Spine-2: 192.168.1.2
  - Leaf-1: 192.168.1.11
  - Leaf-2: 192.168.1.12

### Switch Requirements
- Cisco Nexus 9000 series switches (physical or virtual)
- NX-OS version 7.0(3)I7(1) or higher
- SSH enabled on management interface
- Sufficient user privileges (network-admin role recommended)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ters-golemi/Cisco-NX-OS-VxLAN-Template.git
cd Cisco-NX-OS-VxLAN-Template
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Or manually install the required package:
```bash
pip install netmiko
```

### 3. Verify Configuration Files
Ensure all configuration files are present in the `configs/` directory:
```bash
ls -l configs/
```

You should see:
- spine-1.cfg
- spine-2.cfg
- leaf-1.cfg
- leaf-2.cfg

## Deployment Options

### Option 1: Automated Deployment (Recommended)

#### Deploy to All Devices
```bash
python deploy_vxlan.py -u admin
```
You will be prompted for the password.

#### Deploy to Specific Devices
```bash
python deploy_vxlan.py -u admin -d spine-1 spine-2
```

#### Deploy with Verification
```bash
python deploy_vxlan.py -u admin -v
```

#### Dry Run (Test Without Deploying)
```bash
python deploy_vxlan.py -u admin --dry-run
```

#### Specify Password on Command Line (Not Recommended for Production)
```bash
python deploy_vxlan.py -u admin -p yourpassword
```

### Option 2: Manual Deployment

#### Using SCP/TFTP
1. Copy configuration files to switches:
```bash
scp configs/spine-1.cfg admin@192.168.1.1:spine-1.cfg
```

2. On each switch, apply the configuration:
```
configure terminal
copy bootflash:spine-1.cfg running-config
copy running-config startup-config
```

#### Using Copy-Paste
1. SSH to each switch:
```bash
ssh admin@192.168.1.1
```

2. Enter configuration mode:
```
configure terminal
```

3. Copy and paste the contents of the corresponding config file

4. Save the configuration:
```
copy running-config startup-config
```

## Deployment Order

For best results, follow this order:

1. **Spine Switches First**
   - Deploy Spine-1
   - Deploy Spine-2
   - Wait 2-3 minutes for BGP to stabilize

2. **Leaf Switches Next**
   - Deploy Leaf-1
   - Deploy Leaf-2
   - Wait 2-3 minutes for EVPN to establish

## Post-Deployment Verification

### Automated Verification
The deployment script with `-v` flag will automatically verify:
```bash
python deploy_vxlan.py -u admin -v
```

### Manual Verification

#### On Spine Switches
```bash
# Check BGP status
show bgp summary
show bgp l2vpn evpn summary

# Check BGP EVPN routes
show bgp l2vpn evpn

# Check neighbors
show ip bgp neighbors
```

#### On Leaf Switches
```bash
# Check NVE peers
show nve peers

# Check VxLAN tunnels
show interface nve1

# Check BGP EVPN status
show bgp l2vpn evpn summary

# Check EVPN routes
show bgp l2vpn evpn

# Check VNI status
show vxlan

# Check L2 VNI
show l2route evpn mac all

# Check L3 VNI
show l2route evpn mac-ip all

# Check fabric forwarding
show fabric forwarding
```

### Connectivity Tests
```bash
# From any leaf switch
ping 10.0.0.1 source 10.0.0.11    # Ping Spine-1
ping 10.0.0.2 source 10.0.0.11    # Ping Spine-2
ping 10.0.0.111 source 10.0.0.112 # Ping other VTEP
```

## Expected Results

After successful deployment:

1. **BGP Sessions**: All BGP sessions should be in "Established" state
2. **NVE Peers**: Leaf switches should see each other as NVE peers
3. **EVPN Routes**: Type 2 (MAC-IP), Type 3 (IMET) routes should be present
4. **VNI Status**: All VNIs should be "Up" state

## Troubleshooting

### Common Issues

#### 1. BGP Sessions Not Establishing
```bash
# Check BGP configuration
show run bgp

# Check IP connectivity
ping <neighbor-ip>

# Check BGP neighbors
show ip bgp neighbors
```

#### 2. NVE Peers Not Forming
```bash
# Check NVE interface status
show interface nve1

# Check underlay reachability
ping <vtep-loopback> source loopback1

# Check BGP EVPN routes
show bgp l2vpn evpn
```

#### 3. VNI Not Working
```bash
# Check VNI configuration
show run | include vn-segment

# Check EVPN VNI status
show nve vni

# Check L2 route table
show l2route evpn mac all
```

#### 4. Authentication Failures
- Verify SSH credentials
- Check user permissions (should have network-admin role)
- Verify enable password if required

#### 5. Connection Timeouts
- Verify management IP addresses
- Check network connectivity
- Verify SSH is enabled: `feature ssh`

### Debug Commands
```bash
# Enable BGP debugging (use with caution in production)
debug bgp updates
debug bgp events

# Enable NVE debugging
debug nve

# Enable EVPN debugging
debug bgp l2vpn evpn
```

## Rollback Procedure

### If Issues Occur During Deployment

1. **Restore Previous Configuration**:
```bash
configure replace bootflash:previous-config.cfg
```

2. **Or Reboot to Startup Config**:
```bash
reload
# When prompted, do not save running-config
```

### Create Backup Before Deployment
```bash
# On each switch, backup current configuration
copy running-config bootflash:backup-config-$(date +%Y%m%d).cfg
```

## Security Best Practices

1. **Use Strong Passwords**: Ensure all switches have strong passwords
2. **SSH Keys**: Consider using SSH key authentication
3. **TACACS+/RADIUS**: Use centralized authentication when possible
4. **Management ACLs**: Restrict management access to trusted networks
5. **Change Default Credentials**: Never use default credentials

## Support and Maintenance

### Log Files
- Deployment logs: `<device-name>_session.log`
- Switch logs: Check with `show logging logfile`

### Configuration Backup
Regular backups are recommended:
```bash
# Schedule automatic backups
scheduler schedule daily
  time daily 02:00
  job name backup
    copy running-config bootflash:backup-$(date +%Y%m%d).cfg

# Or use the deployment script to pull configs
```

### Updates and Changes
When making changes:
1. Update the configuration files in `configs/` directory
2. Test in lab environment first
3. Use `--dry-run` to preview changes
4. Deploy during maintenance window
5. Verify after deployment

## Additional Resources

- [Cisco VXLAN BGP EVPN Configuration Guide](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/7-x/vxlan/configuration/guide/b_Cisco_Nexus_9000_Series_NX-OS_VXLAN_Configuration_Guide_7x.html)
- [Netmiko Documentation](https://github.com/ktbyers/netmiko)
- Project Documentation: See README.md, TOPOLOGY.md, and IP_SCHEME.md
