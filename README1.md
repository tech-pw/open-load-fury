# Overview: Distributed Load Testing Setup with JMeter on EC2 Instances

![logo](./images/pw.jpg)

[Physics Wallah](https://www.pw.live/)


## Introduction

This document outlines the setup and execution of a distributed load testing environment using Apache JMeter on Amazon EC2 instances. The purpose is to enable users to perform comprehensive load tests on their applications, simulating real-world scenarios by distributing the load across different geographic regions and availability zones. The entire setup is user-friendly, requiring interaction only through a YAML configuration file.

## Objectives

1. **Automate Load Test Setup**: Streamline the process of setting up a load testing environment using JMeter.
2. **Distributed Load Testing**: Leverage multiple EC2 instances to distribute the load, ensuring robust and scalable testing.
3. **Geographic Distribution**: Allow users to run load tests from various AWS regions and availability zones to simulate diverse user locations.
4. **User-Friendly Interface**: Enable users to configure and manage the entire load testing process through a single YAML file.

## Key Components

1. **Apache JMeter**: An open-source tool for load testing and measuring performance.
2. **Amazon EC2 Instances**: Scalable virtual servers in the AWS cloud.
3. **AWS Regions and Availability Zones**: Different physical locations worldwide where EC2 instances can be launched.
4. **Python Scripts**: Used for provisioning EC2 instances.
5. **Ansible Roles and Playbooks**: Automate the configuration of services, installation of JMeter, execution of load tests, and collection of results.
6. **YAML Configuration File**: Single point of configuration for users to define test parameters and settings.
7. **Operating System Compatibility**: Compatible with both Ubuntu and Red Hat-based machines.

## Implementation Steps

1. **Provision EC2 Instances**:
    - **Python Scripts**: Utilize Python scripts to provision EC2 instances across various regions and availability zones based on the YAML configuration file.
    - **Instance Configuration**: Define instance types, security groups, and other configurations required for the test environment in the YAML file.

### Example YAML Configuration for provisioning EC2 instances

```yaml

instances:
  - region: ap-south-1
    spec:
      ImageId: ami-1234567890
      InstanceType: t3.xlarge
      KeyName: key-name
      SecurityGroupIds:
        - sg-1234567890
      SubnetId: subnet-1234567890
      TagSpecifications:
        - ResourceType: instance
          Tags:
            - Key: Name
              Value: Loadtest

  - region: ap-south-2
    spec:
      ImageId: ami-0987654321
      InstanceType: t3.xlarge
      KeyName: key-name
      SecurityGroupIds:
        - sg-0987654321
      SubnetId: subnet-0987654321
      TagSpecifications:
        - ResourceType: instance
          Tags:
            - Key: Name
              Value: Loadtest
```
2. **Configure Services with Ansible**:
    - **Instance Checks**: Use Ansible to verify that all EC2 instances are running and ready for SSH access.
    - **Install JMeter**: Use Ansible roles to install JMeter on all EC2 instances, including necessary plugins, as specified in the YAML file.
    - **File Distribution**: Copy the JMeter test plan and data files to each EC2 instance as defined in the YAML file.
    - **Heap Dump Memory Update**: Update the heap dump memory settings on each machine to optimize performance for load testing.

### Remote execution configuration
```yaml
remote_execution:
  ssh_key_dir: location to your ssh keys
  ssh_user: 'ubuntu'
  parallel_tasks_limit: 10
  playbook_file: playbook.yaml

```

3. **Automate Load Test Execution**:
    - **Ansible Playbooks**: Use Ansible playbooks to start the JMeter load test on all EC2 instances.
    - **Scripted Execution**: Execute the JMeter tests, collect individual CSV reports from each instance, and generate a final aggregated CSV report.

4. **Post-Test Actions**:
    - **Result Collection**: Use Ansible playbooks to copy all load test CSV reports from the EC2 instances to the host machine.
    - **Report Generation**: Compile the results into a final comprehensive load test report using the aggregated CSV data.
    - **Instance Termination**: Terminate all EC2 instances that were provisioned for performing the load test to optimize costs.

### Load test configuration
```yaml
loadtest:
  name: demo
  instance_count: 1
  jmeter_local_data_dir: data/
  tool: jmeter
  install: true
  jmeter_version: 5.6.3
  jmeter_local_config_dir: jmeter
  jmeter_remote_config_dir: jmeter/
  jmeter_output_file: result.csv
  output_report_dir: loadtest_result
  jmeter_plan_file: plan.jmx

```
5. **Geographic Distribution**:
    - **Regional Testing**: Allow users to specify regions and availability zones for running tests to simulate different user bases through the YAML file.

6. **Monitoring and Reporting**:
    - **Real-Time Monitoring**: Integrate CloudWatch or other monitoring tools to observe test performance in real-time.
    - **Results Aggregation**: Collect and aggregate results from all instances, providing comprehensive reports.

7. **User Interface**:
    - **YAML Configuration**: Enable users to configure tests, including instance details, JMeter settings, and test parameters, through a single YAML file.

## Example configurations

### Minimal configuration

```yaml
instances:
  - region: ap-south-1
    spec:
      ImageId: ami-1234567890
      InstanceType: t3.xlarge
      KeyName: key-name
      SecurityGroupIds:
        - sg-1234567890
      SubnetId: subnet-1234567890
      TagSpecifications:
        - ResourceType: instance
          Tags:
            - Key: Name
              Value: Loadtest

remote_execution:
  ssh_key_dir: location to your ssh keys
  ssh_user: 'ubuntu'

loadtest:
  name: demo
  instance_count: 20
  jmeter_plan_file: plan.jmx

```

## Benefits

- **Scalability**: Easily scale the number of instances up or down based on testing requirements.
- **Flexibility**: Test applications from multiple geographic locations to ensure global performance and reliability.
- **Cost-Effective**: Utilize on-demand or spot instances to optimize costs.
- **Simplicity**: Streamlined user interaction through a single YAML configuration file.

