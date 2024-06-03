
def validate_input(logger, config):
    instance_spec = ['ImageId', 'InstanceType', 'KeyName', 'SecurityGroupIds', 'SubnetId']
    variables_to_check = ['instances', 'loadtest']
    instances_spec = ['region', 'spec']
    loadtest_spec = ['instance_count', 'name']

    for var in variables_to_check:
        try:
            if var in locals()['config']:

                if var == 'loadtest':
                    for key in loadtest_spec:
                        if key not in config['loadtest']:
                            raise NameError(f'{key} is not defined in loadtest: {config["loadtest"]}')

                if var == 'instances':
                    for instance in config['instances']:
                        for instance_key in instances_spec:
                            if instance_key not in instance:
                                print(instance)
                                raise NameError(f'{instance_key} is not defined')

                        if 'spec' in instance:
                            for key in instance_spec:
                                if key not in instance['spec']:
                                    print(instance)
                                    raise NameError(f'{key} is not defined in instances spec')
                            for required_key in instance_spec:
                                if required_key not in instance['spec']:
                                    raise NameError(f'{required_key} is missing in instances spec')
                        else:
                            raise NameError(f'spec is missing in instance')
            else:
                raise NameError(f'{var} is not defined in the configuration file')
        except NameError as e:
            logger.exception(e)
            exit(1)

