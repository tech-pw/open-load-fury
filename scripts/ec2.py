import boto3
from .loadtest import cal_no_instances
import time


class EC2InstanceManager:
    def __init__(
            self,
            logger,
            aws_access_key_id=None,
            aws_secret_access_key=None
        ):

        self.logger = logger
        self.SERVICE = 'ec2'
        self.logger.debug(f"using service {self.SERVICE}")
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key


    def create_instances(self, **kwargs):

        try:
            run_instance_input = kwargs['instances']
            created_instances = []
            num_of_instances = cal_no_instances(self.logger, **kwargs)
            self.logger.info(f"Divided total number of instances into blocks: {num_of_instances}")

            for index, instances in enumerate(run_instance_input):

                ec2_client = boto3.client(
                    self.SERVICE,
                    region_name=instances['region'],
                )

                if 'MinCount' not in instances['spec']:
                    instances['spec']['MinCount'] = 1
                    self.logger.debug(f"MinCount not found in instances at {index} index")
                    self.logger.info(f"Setting MinCount to '1' at {index} index of instances")

                if 'MaxCount' not in instances['spec']:
                    instances['spec']['MaxCount'] = num_of_instances[index]
                    self.logger.info(f"Setting MaxCount to '{num_of_instances[index]}' at {index} index of instances")

                if instances['spec']['MaxCount'] > 0:
                    self.logger.debug(f"Creating instances for {index} index of instances")
                    self.logger.debug(instances['spec'])
                    response = ec2_client.run_instances(**instances['spec'])
                    self.logger.debug('Instances created successfully')
                    for instance in response['Instances']:
                        instance_dict = {}
                        instance_dict['instance_id'] = instance['InstanceId']
                        instance_dict['region'] = instances['region']
                        instance_dict['key_name'] = instance['KeyName']
                        instance_dict['private_ip'] = instance['PrivateIpAddress']
                        created_instances.append(instance_dict)
                        self.logger.info(f'Instance {instance["InstanceId"]} is created')
                        print(f'Instance {instance["InstanceId"]} is created')

            self.logger.debug('Instances created successfully')
            self.logger.debug(created_instances)
            self.logger.info('Waiting for 5 seconds')
            time.sleep(5)
            self.logger.info('Checking instances is in running state')
            running_instances = self.describe_instances(created_instances)
            self.logger.debug('Instances is running state')
            self.logger.debug(running_instances)
            return created_instances, running_instances

        except Exception as err:
            self.logger.exception(f'[Error]: {err}')
            exit(1)


    def describe_instances(self, created_instances):

        retry = 0
        running_instances = []

        while retry < 4:

            instances_grouped = {}

            for instance in created_instances:
                region = instance['region']

                if region not in instances_grouped:
                    instances_grouped[region] = []
                    self.logger.debug(f"Adding {region} region to instances grouped by region")

                instances_grouped[region].append(instance['instance_id'])
                self.logger.debug(f"Adding {instance['instance_id']} instance to {region} region group")

                for region, regional_instances in instances_grouped.items():

                    print(f'Instances in region {region}')
                    self.logger.info(f'Instances in region {region}')

                    ec2_client = boto3.client(
                        self.SERVICE,
                        region_name=region,
                    )
                    if regional_instances:
                        self.logger.debug(f"Checking instances state in {region} region")
                        self.logger.debug(regional_instances)
                        paginator = ec2_client.get_paginator('describe_instances')
                        page_iterator = paginator.paginate(InstanceIds=regional_instances)
                        for page in page_iterator:
                            if 'Reservations' in page:
                                for reservation in page['Reservations']:
                                    if 'Instances' in reservation:
                                        for inst in reservation['Instances']:
                                            state = inst['State']['Name']
                                            print(f"Instance {inst['InstanceId']} is in the {state} state.")
                                            self.logger.info(f"Instance {inst['InstanceId']} is in the {state} state.")
                                            if state == 'running':
                                                instances_grouped[region] = [running_instance for running_instance in regional_instances if running_instance != inst['InstanceId']]
                                                for index, instance in enumerate(created_instances):
                                                    if inst['InstanceId'] == instance['instance_id'] and inst['InstanceId'] not in [instance['instance_id'] for instance in running_instances]:
                                                        if 'PublicIpAddress' in inst:
                                                            self.logger.debug(f'{inst["InstanceId"]} instance having public IP')
                                                            public_ip = inst['PublicIpAddress']
                                                            created_instances[index]['public_ip'] = public_ip
                                                        running_instances.append(created_instances[index])

                                    else:
                                        print(f"No instances found for instance id {instance['instance_id']} in region {instance['region']}")
                                        self.logger.info(f"No instances found for instance id {instance['instance_id']} in region {instance['region']}")
                            else:
                                print(f"No reservations found for instance id {instance['instance_id']} in region {instance['region']}")
                                self.logger.info(f"No reservations found for instance id {instance['instance_id']} in region {instance['region']}")

            if len(created_instances) != len(running_instances):
                retry += 1
                self.logger.info(f'All instances are not in running state retrying: {retry}')
                self.logger.debug('Waiting for 20 seconds)')
                time.sleep(20)
            elif len(created_instances) <= len(running_instances):
                self.logger.info('All instances are in running state')
                break
            else:
                break

        print(f'Requested Instances: {len(created_instances)}')
        self.logger.info(f'Requested Instances: {len(created_instances)}')
        print(f'Running Instances: {len(running_instances)}')
        self.logger.info(f'Running Instances: {len(running_instances)}')

        return running_instances


    def terminate_instances(self, created_instances):

        self.logger.debug('Terminating instances')
        try:
            instances_grouped = {}

            self.logger.debug('Grouping instances by region')
            for instance in created_instances:
                region = instance['region']

                if region not in instances_grouped:
                    instances_grouped[region] = []

                instances_grouped[region].append(instance['instance_id'])

            for region, regional_instances in instances_grouped.items():

                print(f'Instances in region {region}')
                self.logger.info(f'Instances in region {region}')

                ec2_client = boto3.client(
                    self.SERVICE,
                    region_name=region,
                )
                self.logger.debug(f"Terminating instances: {regional_instances}")
                ec2_client.terminate_instances(InstanceIds=regional_instances)
                self.logger.debug(f"Terminated instances: {regional_instances}")

                for instance in regional_instances:
                    print(f'Instance {instance} is terminated')
                    self.logger.info(f'Instance {instance} is terminated')

        except Exception as err:
            self.logger.exception(f'[Error]: {err}')


