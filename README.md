
# Overview: Distributed Load Testing Setup with JMeter on EC2 Instances

![logo](./images/pw.jpg)

[Physics Wallah](https://www.pw.live/)


## Overview

This document outlines the setup and execution of a distributed load testing environment using Apache JMeter on Amazon EC2 instances. The goal is to enable users to perform comprehensive load tests on their applications, simulating real-world scenarios by distributing the load across different geographic regions and availability zones. The entire setup is user-friendly, requiring interaction only through a YAML configuration file.

## Load Test Features

**Action**                          | **Description**                                                                                   | **Supported**                                       
----------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------
Launch EC2 instances                | Launches EC2 instances in different regions and availability zones based on [user inputs](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/run_instances.html) | Yes
Install Apache JMeter               | Optionally installs specific versions of JMeter on Debian and RedHat-based OS | Yes
Install JMeter plugins              | Optionally downloads plugins and places them in the *jmeter-plugins* directory | Yes
Jmeter Heap                            | Allows you to update Jmeter heap settings | Yes
Download individual reports and Merge individual reports         | Collects individual reports from remote machines  and Merges individual reports and creates a combined CSV report| Yes
Create final HTML report            | Generates a final HTML report using the CSV report | Yes
Upload final HTML report to S3 bucket | Uploads the final HTML report to an S3 bucket | Yes


## Structure

```
├── jmeter            # Load test configuration files, such as plan.jmx
├── jmeter_plugins    # Additional JMeter plugins
├── loadtest-role     # Ansible role for configuring services and running the load test
├── scripts           # Python scripts
│   ├── data_file.py  # For splitting data files
│   ├── ec2.py        # For launching EC2 instances, checking instance status, and terminating instances
│   ├── get_data.py   # For reading the YAML file
│   ├── loadtest.py   # For merging load test reports and distributing EC2 instances
│   ├── logger.py     # For logging
│   ├── s3.py         # For sending reports to an S3 bucket
│   ├── scm.py        # For creating inventory files and running Ansible
│   └── validations.py # For validation functions
├── ssh_keys          # SSH private PEM key
```



## Prerequisites
  - **AWS Account:** You need an active AWS account to utilize AWS services.
  - **Python Environment:** Ensure Python is installed on your local machine or server. Download Python from the official Python website and follow the installation instructions for your operating system.
  - **AWS CLI:** Install the AWS Command Line Interface (CLI) tool to interact with AWS services from the command line. Refer to the AWS CLI documentation for installation instructions.
  - **AWS IAM Credentials:** Obtain AWS Identity and Access Management (IAM) credentials with appropriate permissions to launch, describe, and terminate EC2 instances and put object to S3 bucket if you want to upload final report to S3.
  - **Additional Libraries:** Install additional libraries using pip. Run `pip3 install -r requirements.txt` in your terminal or command prompt.

## Requirements

| Name       | Version |
|------------|---------|
| AWS        | >= 2.0  |
| Python     | >= 3.0  |

## Providers

| Name       | Version |
|------------|---------|
| AWS        | >= 2.0  |


## Configuration Parameters

### instances
| Name | Description | Type | Required |
|------|-------------|------|:--------:|
| `region` | AWS region where the EC2 instances will be launched | string | Yes |
| `spec` | EC2 instance specifications for more specs for the [boto3 run_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/run_instances.html) | dict | Yes |
| `spec.ImageId` | ID of the AMI to use for the instance | string | Yes |
| `spec.InstanceType` | Type of the EC2 instance | string | Yes |
| `spec.KeyName` | Name of the key pair | string | Yes |
| `spec.SecurityGroupIds` | List of security group IDs | list | Yes |
| `spec.SubnetId` | ID of the subnet | string | Yes |
| `spec.TagSpecifications` | Tags to apply to the instances | list | No |
| `spec.TagSpecifications.ResourceType` | Type of the resource to tag | string | No |
| `spec.TagSpecifications.Tags` | List of tags | list | No |
| `spec.TagSpecifications.Tags.Key` | Tag key | string | No |
| `spec.TagSpecifications.Tags.Value` | Tag value | string | No |

### loadtest
| Name | Description | Type | Required |
|------|-------------|------|:--------:|
| `name` | Name for the load test, used for uploading the final report to S3 | string | No |
| `instance_count` | Number of EC2 instances to use for the load test | int | Yes |
| `jmeter_local_data_dir` | Local directory for JMeter data | string | No |
| `tool` | Tool to use for the load test (e.g., JMeter) | string | No |
| `install` | Flag to indicate whether to install the tool | bool | No |
| `jmeter_version` | Version of JMeter to use | string | No |
| `jmeter_local_config_dir` | Local directory for JMeter configuration | string | No |
| `jmeter_remote_config_dir` | Remote directory for JMeter configuration | string | No |
| `jmeter_output_file` | Output file for JMeter results | string | No |
| `output_report_dir` | Directory to store the load test results | string | No |
| `jmeter_plan_file` | JMeter test plan file | string | No |

### remote_execution
| Name | Description | Type | Required |
|------|-------------|------|:--------:|
| `ssh_key_dir` | Directory for SSH keys | string | Yes |
| `ssh_user` | SSH user to connect to the instances | string | Yes |
| `parallel_tasks_limit` | Limit for parallel tasks execution | int | No |
| `playbook_file` | Ansible playbook file | string | No |

### log_file_path
| Name | Description | Type | Required |
|------|-------------|------|:--------:|
| `log_file_path` | Path to the log file | string | No |

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

## Usage

### Running Locally with Python
Ensure you have Python and the required dependencies installed:

```
pip install -r requirements.txt
```

For running load test
:```
python3 main.py -f your_config_file.yaml
```


## Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we as
contributors and maintainers pledge to making participation in our project and
our community a harassment-free experience for everyone, regardless of age, body
size, disability, ethnicity, gender identity and expression, level of experience,
nationality, personal appearance, race, religion, or sexual identity and
orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment
include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery and unwelcome sexual attention or
advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or electronic
  address, without explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

### Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable
behavior and are expected to take appropriate and fair corrective action in
response to any instances of unacceptable behavior.

Project maintainers have the right and responsibility to remove, edit, or
reject comments, commits, code, wiki edits, issues, and other contributions
that are not aligned to this Code of Conduct, or to ban temporarily or
permanently any contributor for other behaviors that they deem inappropriate,
threatening, offensive, or harmful.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.


