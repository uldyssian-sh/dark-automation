#!/usr/bin/env python3
"""
AWS CloudFormation Template Generator
Enterprise-grade CloudFormation template generation with best practices.

Use of this code is at your own risk.
Author bears no responsibility for any damages caused by the code.
"""

import json
import yaml
import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from datetime import datetime
import boto3
from jinja2 import Environment, FileSystemLoader, Template

class ResourceType(Enum):
    """AWS CloudFormation resource types."""
    VPC = "AWS::EC2::VPC"
    SUBNET = "AWS::EC2::Subnet"
    INTERNET_GATEWAY = "AWS::EC2::InternetGateway"
    ROUTE_TABLE = "AWS::EC2::RouteTable"
    SECURITY_GROUP = "AWS::EC2::SecurityGroup"
    EC2_INSTANCE = "AWS::EC2::Instance"
    RDS_INSTANCE = "AWS::RDS::DBInstance"
    LOAD_BALANCER = "AWS::ElasticLoadBalancingV2::LoadBalancer"
    TARGET_GROUP = "AWS::ElasticLoadBalancingV2::TargetGroup"
    LAMBDA_FUNCTION = "AWS::Lambda::Function"
    S3_BUCKET = "AWS::S3::Bucket"
    IAM_ROLE = "AWS::IAM::Role"
    IAM_POLICY = "AWS::IAM::Policy"
    CLOUDWATCH_ALARM = "AWS::CloudWatch::Alarm"
    SNS_TOPIC = "AWS::SNS::Topic"

class TemplateFormat(Enum):
    """CloudFormation template formats."""
    JSON = "json"
    YAML = "yaml"

@dataclass
class Parameter:
    """CloudFormation parameter definition."""
    name: str
    type: str
    description: str
    default: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    constraint_description: Optional[str] = None

@dataclass
class Output:
    """CloudFormation output definition."""
    name: str
    description: str
    value: str
    export_name: Optional[str] = None

@dataclass
class Resource:
    """CloudFormation resource definition."""
    logical_id: str
    type: ResourceType
    properties: Dict[str, Any]
    depends_on: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    condition: Optional[str] = None

class CloudFormationGenerator:
    """
    Enterprise-grade AWS CloudFormation template generator.
    Supports complex infrastructure patterns with security best practices.
    """
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        self.logger = self._setup_logging()
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        self.template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "",
            "Parameters": {},
            "Mappings": {},
            "Conditions": {},
            "Resources": {},
            "Outputs": {}
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for CloudFormation generator."""
        logger = logging.getLogger('CloudFormationGenerator')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def set_description(self, description: str):
        """Set template description."""
        self.template["Description"] = description
    
    def add_parameter(self, parameter: Parameter):
        """Add parameter to template."""
        param_def = {
            "Type": parameter.type,
            "Description": parameter.description
        }
        
        if parameter.default:
            param_def["Default"] = parameter.default
        if parameter.allowed_values:
            param_def["AllowedValues"] = parameter.allowed_values
        if parameter.min_length:
            param_def["MinLength"] = parameter.min_length
        if parameter.max_length:
            param_def["MaxLength"] = parameter.max_length
        if parameter.constraint_description:
            param_def["ConstraintDescription"] = parameter.constraint_description
            
        self.template["Parameters"][parameter.name] = param_def
    
    def add_resource(self, resource: Resource):
        """Add resource to template."""
        resource_def = {
            "Type": resource.type.value,
            "Properties": resource.properties
        }
        
        if resource.depends_on:
            resource_def["DependsOn"] = resource.depends_on
        if resource.metadata:
            resource_def["Metadata"] = resource.metadata
        if resource.condition:
            resource_def["Condition"] = resource.condition
            
        self.template["Resources"][resource.logical_id] = resource_def
    
    def add_output(self, output: Output):
        """Add output to template."""
        output_def = {
            "Description": output.description,
            "Value": output.value
        }
        
        if output.export_name:
            output_def["Export"] = {"Name": output.export_name}
            
        self.template["Outputs"][output.name] = output_def
    
    def generate_vpc_infrastructure(self, vpc_cidr: str = "10.0.0.0/16",
                                  availability_zones: int = 2) -> Dict[str, Any]:
        """
        Generate VPC infrastructure with best practices.
        
        Args:
            vpc_cidr: CIDR block for VPC
            availability_zones: Number of AZs to use
            
        Returns:
            Dictionary with generated resources
        """
        self.logger.info(f"Generating VPC infrastructure with {availability_zones} AZs")
        
        # VPC
        vpc_resource = Resource(
            logical_id="VPC",
            type=ResourceType.VPC,
            properties={
                "CidrBlock": vpc_cidr,
                "EnableDnsHostnames": True,
                "EnableDnsSupport": True,
                "Tags": [
                    {"Key": "Name", "Value": {"Ref": "AWS::StackName"}},
                    {"Key": "Environment", "Value": {"Ref": "Environment"}}
                ]
            }
        )
        self.add_resource(vpc_resource)
        
        # Internet Gateway
        igw_resource = Resource(
            logical_id="InternetGateway",
            type=ResourceType.INTERNET_GATEWAY,
            properties={
                "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-IGW"}}]
            }
        )
        self.add_resource(igw_resource)
        
        # Attach IGW to VPC
        igw_attachment = Resource(
            logical_id="InternetGatewayAttachment",
            type="AWS::EC2::VPCGatewayAttachment",
            properties={
                "InternetGatewayId": {"Ref": "InternetGateway"},
                "VpcId": {"Ref": "VPC"}
            }
        )
        self.add_resource(igw_attachment)
        
        # Public and Private Subnets
        for az in range(availability_zones):
            az_letter = chr(ord('a') + az)
            
            # Public Subnet
            public_subnet = Resource(
                logical_id=f"PublicSubnet{az + 1}",
                type=ResourceType.SUBNET,
                properties={
                    "VpcId": {"Ref": "VPC"},
                    "AvailabilityZone": {"Fn::Sub": f"${{AWS::Region}}{az_letter}"},
                    "CidrBlock": f"10.0.{az * 2 + 1}.0/24",
                    "MapPublicIpOnLaunch": True,
                    "Tags": [
                        {"Key": "Name", "Value": {"Fn::Sub": f"${{AWS::StackName}}-Public-Subnet-{az + 1}"}},
                        {"Key": "Type", "Value": "Public"}
                    ]
                }
            )
            self.add_resource(public_subnet)
            
            # Private Subnet
            private_subnet = Resource(
                logical_id=f"PrivateSubnet{az + 1}",
                type=ResourceType.SUBNET,
                properties={
                    "VpcId": {"Ref": "VPC"},
                    "AvailabilityZone": {"Fn::Sub": f"${{AWS::Region}}{az_letter}"},
                    "CidrBlock": f"10.0.{az * 2 + 2}.0/24",
                    "Tags": [
                        {"Key": "Name", "Value": {"Fn::Sub": f"${{AWS::StackName}}-Private-Subnet-{az + 1}"}},
                        {"Key": "Type", "Value": "Private"}
                    ]
                }
            )
            self.add_resource(private_subnet)
        
        # Public Route Table
        public_route_table = Resource(
            logical_id="PublicRouteTable",
            type=ResourceType.ROUTE_TABLE,
            properties={
                "VpcId": {"Ref": "VPC"},
                "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-Public-Routes"}}]
            }
        )
        self.add_resource(public_route_table)
        
        # Default Public Route
        public_route = Resource(
            logical_id="DefaultPublicRoute",
            type="AWS::EC2::Route",
            properties={
                "RouteTableId": {"Ref": "PublicRouteTable"},
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": {"Ref": "InternetGateway"}
            },
            depends_on=["InternetGatewayAttachment"]
        )
        self.add_resource(public_route)
        
        # Associate public subnets with public route table
        for az in range(availability_zones):
            association = Resource(
                logical_id=f"PublicSubnet{az + 1}RouteTableAssociation",
                type="AWS::EC2::SubnetRouteTableAssociation",
                properties={
                    "RouteTableId": {"Ref": "PublicRouteTable"},
                    "SubnetId": {"Ref": f"PublicSubnet{az + 1}"}
                }
            )
            self.add_resource(association)
        
        return {"vpc_id": "VPC", "public_subnets": [f"PublicSubnet{i+1}" for i in range(availability_zones)],
                "private_subnets": [f"PrivateSubnet{i+1}" for i in range(availability_zones)]}
    
    def generate_web_tier(self, instance_type: str = "t3.medium",
                         min_size: int = 2, max_size: int = 10) -> Dict[str, Any]:
        """
        Generate web tier with Auto Scaling and Load Balancer.
        
        Args:
            instance_type: EC2 instance type
            min_size: Minimum instances in ASG
            max_size: Maximum instances in ASG
            
        Returns:
            Dictionary with generated resources
        """
        self.logger.info("Generating web tier infrastructure")
        
        # Security Group for Web Servers
        web_sg = Resource(
            logical_id="WebServerSecurityGroup",
            type=ResourceType.SECURITY_GROUP,
            properties={
                "GroupDescription": "Security group for web servers",
                "VpcId": {"Ref": "VPC"},
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 80,
                        "ToPort": 80,
                        "SourceSecurityGroupId": {"Ref": "LoadBalancerSecurityGroup"}
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "SourceSecurityGroupId": {"Ref": "LoadBalancerSecurityGroup"}
                    }
                ],
                "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-WebServer-SG"}}]
            }
        )
        self.add_resource(web_sg)
        
        # Security Group for Load Balancer
        lb_sg = Resource(
            logical_id="LoadBalancerSecurityGroup",
            type=ResourceType.SECURITY_GROUP,
            properties={
                "GroupDescription": "Security group for load balancer",
                "VpcId": {"Ref": "VPC"},
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 80,
                        "ToPort": 80,
                        "CidrIp": "0.0.0.0/0"
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "CidrIp": "0.0.0.0/0"
                    }
                ],
                "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-LoadBalancer-SG"}}]
            }
        )
        self.add_resource(lb_sg)
        
        # Application Load Balancer
        alb = Resource(
            logical_id="ApplicationLoadBalancer",
            type=ResourceType.LOAD_BALANCER,
            properties={
                "Type": "application",
                "Scheme": "internet-facing",
                "SecurityGroups": [{"Ref": "LoadBalancerSecurityGroup"}],
                "Subnets": [{"Ref": "PublicSubnet1"}, {"Ref": "PublicSubnet2"}],
                "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-ALB"}}]
            }
        )
        self.add_resource(alb)
        
        # Target Group
        target_group = Resource(
            logical_id="WebServerTargetGroup",
            type=ResourceType.TARGET_GROUP,
            properties={
                "Port": 80,
                "Protocol": "HTTP",
                "VpcId": {"Ref": "VPC"},
                "HealthCheckPath": "/health",
                "HealthCheckProtocol": "HTTP",
                "HealthCheckIntervalSeconds": 30,
                "HealthyThresholdCount": 2,
                "UnhealthyThresholdCount": 5,
                "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-WebServer-TG"}}]
            }
        )
        self.add_resource(target_group)
        
        # Listener
        listener = Resource(
            logical_id="LoadBalancerListener",
            type="AWS::ElasticLoadBalancingV2::Listener",
            properties={
                "DefaultActions": [{
                    "Type": "forward",
                    "TargetGroupArn": {"Ref": "WebServerTargetGroup"}
                }],
                "LoadBalancerArn": {"Ref": "ApplicationLoadBalancer"},
                "Port": 80,
                "Protocol": "HTTP"
            }
        )
        self.add_resource(listener)
        
        # Launch Template
        launch_template = Resource(
            logical_id="WebServerLaunchTemplate",
            type="AWS::EC2::LaunchTemplate",
            properties={
                "LaunchTemplateName": {"Fn::Sub": "${AWS::StackName}-WebServer-LaunchTemplate"},
                "LaunchTemplateData": {
                    "ImageId": {"Ref": "LatestAmiId"},
                    "InstanceType": instance_type,
                    "SecurityGroupIds": [{"Ref": "WebServerSecurityGroup"}],
                    "IamInstanceProfile": {"Arn": {"Fn::GetAtt": ["WebServerInstanceProfile", "Arn"]}},
                    "UserData": {
                        "Fn::Base64": {
                            "Fn::Sub": """#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo '<h1>Hello from ${AWS::Region}</h1>' > /var/www/html/index.html
echo 'OK' > /var/www/html/health
"""
                        }
                    },
                    "TagSpecifications": [{
                        "ResourceType": "instance",
                        "Tags": [
                            {"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-WebServer"}},
                            {"Key": "Environment", "Value": {"Ref": "Environment"}}
                        ]
                    }]
                }
            }
        )
        self.add_resource(launch_template)
        
        # Auto Scaling Group
        asg = Resource(
            logical_id="WebServerAutoScalingGroup",
            type="AWS::AutoScaling::AutoScalingGroup",
            properties={
                "VPCZoneIdentifier": [{"Ref": "PrivateSubnet1"}, {"Ref": "PrivateSubnet2"}],
                "LaunchTemplate": {
                    "LaunchTemplateId": {"Ref": "WebServerLaunchTemplate"},
                    "Version": {"Fn::GetAtt": ["WebServerLaunchTemplate", "LatestVersionNumber"]}
                },
                "MinSize": str(min_size),
                "MaxSize": str(max_size),
                "DesiredCapacity": str(min_size),
                "TargetGroupARNs": [{"Ref": "WebServerTargetGroup"}],
                "HealthCheckType": "ELB",
                "HealthCheckGracePeriod": 300,
                "Tags": [{
                    "Key": "Name",
                    "Value": {"Fn::Sub": "${AWS::StackName}-WebServer-ASG"},
                    "PropagateAtLaunch": False
                }]
            }
        )
        self.add_resource(asg)
        
        return {
            "load_balancer": "ApplicationLoadBalancer",
            "target_group": "WebServerTargetGroup",
            "auto_scaling_group": "WebServerAutoScalingGroup"
        }
    
    def generate_database_tier(self, engine: str = "postgres",
                             instance_class: str = "db.t3.micro",
                             multi_az: bool = True) -> Dict[str, Any]:
        """
        Generate database tier with RDS and security best practices.
        
        Args:
            engine: Database engine (postgres, mysql, etc.)
            instance_class: RDS instance class
            multi_az: Enable Multi-AZ deployment
            
        Returns:
            Dictionary with generated resources
        """
        self.logger.info(f"Generating database tier with {engine}")
        
        # Database Security Group
        db_sg = Resource(
            logical_id="DatabaseSecurityGroup",
            type=ResourceType.SECURITY_GROUP,
            properties={
                "GroupDescription": "Security group for database",
                "VpcId": {"Ref": "VPC"},
                "SecurityGroupIngress": [{
                    "IpProtocol": "tcp",
                    "FromPort": 5432 if engine == "postgres" else 3306,
                    "ToPort": 5432 if engine == "postgres" else 3306,
                    "SourceSecurityGroupId": {"Ref": "WebServerSecurityGroup"}
                }],
                "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-Database-SG"}}]
            }
        )
        self.add_resource(db_sg)
        
        # DB Subnet Group
        db_subnet_group = Resource(
            logical_id="DatabaseSubnetGroup",
            type="AWS::RDS::DBSubnetGroup",
            properties={
                "DBSubnetGroupDescription": "Subnet group for RDS database",
                "SubnetIds": [{"Ref": "PrivateSubnet1"}, {"Ref": "PrivateSubnet2"}],
                "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-DB-SubnetGroup"}}]
            }
        )
        self.add_resource(db_subnet_group)
        
        # RDS Instance
        rds_instance = Resource(
            logical_id="DatabaseInstance",
            type=ResourceType.RDS_INSTANCE,
            properties={
                "DBInstanceIdentifier": {"Fn::Sub": "${AWS::StackName}-database"},
                "DBInstanceClass": instance_class,
                "Engine": engine,
                "EngineVersion": "13.7" if engine == "postgres" else "8.0.28",
                "AllocatedStorage": "20",
                "StorageType": "gp2",
                "StorageEncrypted": True,
                "MultiAZ": multi_az,
                "DBSubnetGroupName": {"Ref": "DatabaseSubnetGroup"},
                "VPCSecurityGroups": [{"Ref": "DatabaseSecurityGroup"}],
                "MasterUsername": {"Ref": "DatabaseUsername"},
                "MasterUserPassword": {"Ref": "DatabasePassword"},
                "BackupRetentionPeriod": 7,
                "PreferredBackupWindow": "03:00-04:00",
                "PreferredMaintenanceWindow": "sun:04:00-sun:05:00",
                "DeletionProtection": True,
                "Tags": [
                    {"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-Database"}},
                    {"Key": "Environment", "Value": {"Ref": "Environment"}}
                ]
            }
        )
        self.add_resource(rds_instance)
        
        return {"database_instance": "DatabaseInstance", "database_security_group": "DatabaseSecurityGroup"}
    
    def add_monitoring_and_alerting(self):
        """Add CloudWatch monitoring and SNS alerting."""
        self.logger.info("Adding monitoring and alerting resources")
        
        # SNS Topic for Alerts
        sns_topic = Resource(
            logical_id="AlertsTopic",
            type=ResourceType.SNS_TOPIC,
            properties={
                "TopicName": {"Fn::Sub": "${AWS::StackName}-Alerts"},
                "DisplayName": "Infrastructure Alerts"
            }
        )
        self.add_resource(sns_topic)
        
        # CloudWatch Alarms
        alarms = [
            {
                "name": "HighCPUAlarm",
                "metric": "CPUUtilization",
                "threshold": 80,
                "comparison": "GreaterThanThreshold",
                "description": "High CPU utilization detected"
            },
            {
                "name": "HighMemoryAlarm", 
                "metric": "MemoryUtilization",
                "threshold": 85,
                "comparison": "GreaterThanThreshold",
                "description": "High memory utilization detected"
            }
        ]
        
        for alarm_config in alarms:
            alarm = Resource(
                logical_id=alarm_config["name"],
                type=ResourceType.CLOUDWATCH_ALARM,
                properties={
                    "AlarmDescription": alarm_config["description"],
                    "MetricName": alarm_config["metric"],
                    "Namespace": "AWS/EC2",
                    "Statistic": "Average",
                    "Period": 300,
                    "EvaluationPeriods": 2,
                    "Threshold": alarm_config["threshold"],
                    "ComparisonOperator": alarm_config["comparison"],
                    "AlarmActions": [{"Ref": "AlertsTopic"}]
                }
            )
            self.add_resource(alarm)
    
    def generate_template(self, format: TemplateFormat = TemplateFormat.YAML) -> str:
        """
        Generate CloudFormation template in specified format.
        
        Args:
            format: Output format (JSON or YAML)
            
        Returns:
            Template as string
        """
        if format == TemplateFormat.JSON:
            return json.dumps(self.template, indent=2)
        else:
            return yaml.dump(self.template, default_flow_style=False, sort_keys=False)
    
    def save_template(self, filename: str, format: TemplateFormat = TemplateFormat.YAML):
        """Save template to file."""
        template_content = self.generate_template(format)
        
        with open(filename, 'w') as f:
            f.write(template_content)
        
        self.logger.info(f"Template saved to {filename}")
    
    def validate_template(self) -> Dict[str, Any]:
        """Validate CloudFormation template using AWS API."""
        try:
            cf_client = boto3.client('cloudformation')
            template_body = self.generate_template(TemplateFormat.JSON)
            
            response = cf_client.validate_template(TemplateBody=template_body)
            
            return {
                "valid": True,
                "description": response.get("Description", ""),
                "parameters": response.get("Parameters", []),
                "capabilities": response.get("Capabilities", [])
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }


def create_three_tier_architecture():
    """Create a complete three-tier web application architecture."""
    generator = CloudFormationGenerator()
    
    # Set template description
    generator.set_description("Three-tier web application infrastructure with best practices")
    
    # Add parameters
    parameters = [
        Parameter("Environment", "String", "Environment name", "dev", ["dev", "staging", "prod"]),
        Parameter("InstanceType", "String", "EC2 instance type", "t3.medium"),
        Parameter("DatabaseUsername", "String", "Database master username", "admin"),
        Parameter("DatabasePassword", "String", "Database master password", constraint_description="Must be 8-128 characters"),
        Parameter("LatestAmiId", "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>", 
                 "Latest Amazon Linux AMI ID", "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2")
    ]
    
    for param in parameters:
        generator.add_parameter(param)
    
    # Generate infrastructure tiers
    vpc_resources = generator.generate_vpc_infrastructure()
    web_resources = generator.generate_web_tier()
    db_resources = generator.generate_database_tier()
    
    # Add monitoring
    generator.add_monitoring_and_alerting()
    
    # Add outputs
    outputs = [
        Output("VPCId", "VPC ID", {"Ref": "VPC"}, f"{generator.template.get('Parameters', {}).get('Environment', {}).get('Default', 'dev')}-VPC-ID"),
        Output("LoadBalancerDNS", "Load Balancer DNS Name", {"Fn::GetAtt": ["ApplicationLoadBalancer", "DNSName"]}),
        Output("DatabaseEndpoint", "Database Endpoint", {"Fn::GetAtt": ["DatabaseInstance", "Endpoint.Address"]})
    ]
    
    for output in outputs:
        generator.add_output(output)
    
    return generator


if __name__ == "__main__":
    # Generate three-tier architecture
    generator = create_three_tier_architecture()
    
    # Save template
    generator.save_template("three-tier-architecture.yaml")
    
    # Validate template (requires AWS credentials)
    try:
        validation_result = generator.validate_template()
        if validation_result["valid"]:
            print("✅ Template validation successful")
        else:
            print(f"❌ Template validation failed: {validation_result['error']}")
    except Exception as e:
        print(f"⚠️  Could not validate template: {e}")
    
    print("CloudFormation template generated successfully!")