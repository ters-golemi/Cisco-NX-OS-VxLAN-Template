#!/usr/bin/env python3
"""
VxLAN EVPN Deployment Script for Cisco Nexus Switches
This script automates the deployment of VxLAN/EVPN configurations
to Cisco Nexus spine and leaf switches.

Author: VxLAN Automation
Version: 1.0
"""

import sys
import time
import getpass
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
import argparse
import os


class VxLANDeployer:
    """Class to handle VxLAN/EVPN configuration deployment"""
    
    def __init__(self, username, password, enable_password=None):
        """
        Initialize the deployer with credentials
        
        Args:
            username (str): SSH username
            password (str): SSH password
            enable_password (str): Enable password (optional)
        """
        self.username = username
        self.password = password
        self.enable_password = enable_password if enable_password else password
        self.devices = {
            'spine-1': {
                'host': '192.168.1.1',
                'config_file': 'configs/spine-1.cfg'
            },
            'spine-2': {
                'host': '192.168.1.2',
                'config_file': 'configs/spine-2.cfg'
            },
            'leaf-1': {
                'host': '192.168.1.11',
                'config_file': 'configs/leaf-1.cfg'
            },
            'leaf-2': {
                'host': '192.168.1.12',
                'config_file': 'configs/leaf-2.cfg'
            }
        }
    
    def read_config_file(self, filepath):
        """
        Read configuration file
        
        Args:
            filepath (str): Path to configuration file
            
        Returns:
            list: List of configuration commands
        """
        try:
            with open(filepath, 'r') as f:
                config_lines = f.readlines()
            
            # Remove comments and empty lines
            commands = []
            for line in config_lines:
                line = line.strip()
                if line and not line.startswith('!'):
                    commands.append(line)
            
            return commands
        except FileNotFoundError:
            print(f"Error: Configuration file {filepath} not found")
            return None
        except Exception as e:
            print(f"Error reading configuration file: {str(e)}")
            return None
    
    def connect_to_device(self, device_name, device_info):
        """
        Establish SSH connection to device
        
        Args:
            device_name (str): Name of the device
            device_info (dict): Device connection information
            
        Returns:
            object: Netmiko connection object or None
        """
        device_params = {
            'device_type': 'cisco_nxos',
            'host': device_info['host'],
            'username': self.username,
            'password': self.password,
            'secret': self.enable_password,
            'timeout': 60,
            'session_log': f'{device_name}_session.log'
        }
        
        try:
            print(f"\nConnecting to {device_name} ({device_info['host']})...")
            connection = ConnectHandler(**device_params)
            print(f"Successfully connected to {device_name}")
            return connection
        except NetmikoTimeoutException:
            print(f"Error: Connection timeout for {device_name}")
            return None
        except NetmikoAuthenticationException:
            print(f"Error: Authentication failed for {device_name}")
            return None
        except Exception as e:
            print(f"Error connecting to {device_name}: {str(e)}")
            return None
    
    def deploy_config(self, connection, device_name, commands):
        """
        Deploy configuration to device
        
        Args:
            connection: Netmiko connection object
            device_name (str): Name of the device
            commands (list): List of configuration commands
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"\nDeploying configuration to {device_name}...")
            
            # Enter configuration mode
            connection.enable()
            
            # Send configuration commands
            output = connection.send_config_set(commands, exit_config_mode=False)
            print(f"Configuration applied to {device_name}")
            
            # Save configuration
            print(f"Saving configuration on {device_name}...")
            save_output = connection.send_command_timing('copy running-config startup-config')
            
            # Handle confirmation prompt if it appears
            if 'overwrite' in save_output.lower() or '[y/n]' in save_output.lower():
                save_output += connection.send_command_timing('y')
            
            print(f"Configuration saved on {device_name}")
            
            return True
        except Exception as e:
            print(f"Error deploying configuration to {device_name}: {str(e)}")
            return False
    
    def verify_deployment(self, connection, device_name):
        """
        Verify deployment on device
        
        Args:
            connection: Netmiko connection object
            device_name (str): Name of the device
        """
        try:
            print(f"\n{'='*60}")
            print(f"Verification for {device_name}")
            print(f"{'='*60}")
            
            # Basic verification commands
            commands = [
                'show version | include Software',
                'show ip interface brief',
                'show bgp summary'
            ]
            
            # Add VxLAN-specific commands for leaf switches
            if 'leaf' in device_name.lower():
                commands.extend([
                    'show nve peers',
                    'show bgp l2vpn evpn summary'
                ])
            
            for cmd in commands:
                try:
                    print(f"\n{cmd}:")
                    print("-" * 60)
                    output = connection.send_command(cmd)
                    print(output)
                except Exception as e:
                    print(f"Error executing {cmd}: {str(e)}")
                    
        except Exception as e:
            print(f"Error during verification: {str(e)}")
    
    def deploy_all(self, devices_to_deploy=None, verify=False):
        """
        Deploy configuration to all specified devices
        
        Args:
            devices_to_deploy (list): List of device names to deploy to
            verify (bool): Whether to verify deployment
            
        Returns:
            dict: Results of deployment
        """
        if devices_to_deploy is None:
            devices_to_deploy = list(self.devices.keys())
        
        results = {}
        
        for device_name in devices_to_deploy:
            if device_name not in self.devices:
                print(f"Warning: Device {device_name} not found in device list")
                continue
            
            device_info = self.devices[device_name]
            
            # Read configuration file
            commands = self.read_config_file(device_info['config_file'])
            if commands is None:
                results[device_name] = {'success': False, 'error': 'Config file error'}
                continue
            
            # Connect to device
            connection = self.connect_to_device(device_name, device_info)
            if connection is None:
                results[device_name] = {'success': False, 'error': 'Connection failed'}
                continue
            
            # Deploy configuration
            success = self.deploy_config(connection, device_name, commands)
            results[device_name] = {'success': success}
            
            # Verify deployment if requested
            if verify and success:
                self.verify_deployment(connection, device_name)
            
            # Disconnect
            connection.disconnect()
            print(f"\nDisconnected from {device_name}")
            
            # Brief pause between devices
            time.sleep(2)
        
        return results
    
    def print_summary(self, results):
        """
        Print deployment summary
        
        Args:
            results (dict): Deployment results
        """
        print("\n" + "="*60)
        print("DEPLOYMENT SUMMARY")
        print("="*60)
        
        for device_name, result in results.items():
            status = "SUCCESS" if result['success'] else "FAILED"
            error = f" - {result.get('error', '')}" if not result['success'] else ""
            print(f"{device_name:15s}: {status}{error}")
        
        print("="*60)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Deploy VxLAN/EVPN configuration to Cisco Nexus switches',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Deploy to all devices:
    python deploy_vxlan.py -u admin
  
  Deploy to specific devices:
    python deploy_vxlan.py -u admin -d spine-1 leaf-1
  
  Deploy and verify:
    python deploy_vxlan.py -u admin -v
        """
    )
    
    parser.add_argument('-u', '--username', required=True,
                        help='SSH username')
    parser.add_argument('-p', '--password',
                        help='SSH password (will prompt if not provided)')
    parser.add_argument('-e', '--enable-password',
                        help='Enable password (will use SSH password if not provided)')
    parser.add_argument('-d', '--devices', nargs='+',
                        choices=['spine-1', 'spine-2', 'leaf-1', 'leaf-2'],
                        help='Specific devices to deploy to (default: all)')
    parser.add_argument('-v', '--verify', action='store_true',
                        help='Verify deployment after configuration')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be deployed without actually deploying')
    
    args = parser.parse_args()
    
    # Get password if not provided
    password = args.password
    if not password:
        password = getpass.getpass('Enter SSH password: ')
    
    # Get enable password if not provided
    enable_password = args.enable_password
    if not enable_password:
        enable_password = password
    
    # Create deployer instance
    deployer = VxLANDeployer(args.username, password, enable_password)
    
    # Dry run mode
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print("\nDevices to be configured:")
        devices = args.devices if args.devices else list(deployer.devices.keys())
        for device in devices:
            if device in deployer.devices:
                info = deployer.devices[device]
                print(f"  {device}: {info['host']} - {info['config_file']}")
        return
    
    # Deploy configurations
    print("\n" + "="*60)
    print("VxLAN/EVPN Configuration Deployment")
    print("="*60)
    
    results = deployer.deploy_all(args.devices, args.verify)
    
    # Print summary
    deployer.print_summary(results)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDeployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)
