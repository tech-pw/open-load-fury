# from .get_data import read_yaml
import os
import csv

def cal_no_instances(logger, **kwargs):
    logger.debug("Dividing total number of instances")
    config_output = kwargs
    requested_instances = int(config_output['loadtest']['instance_count']) - sum([int(instances['spec']['MaxCount']) for instances in config_output['instances'] if 'MaxCount' in instances['spec']])

    available_config_blocks = len([instances for instances in config_output['instances'] if 'MaxCount' not in instances['spec']])

    logger.debug(f"{requested_instances} instances were divided into {available_config_blocks} blocks")

    equal_no_instances = requested_instances // available_config_blocks
    remaining_instances = requested_instances % available_config_blocks

    instances_per_blocks = []

    for _, instances in enumerate(config_output['instances']):
        if 'MaxCount' in instances['spec']:
            instances_per_blocks.append(instances['spec']['MaxCount'])
        else:
            if remaining_instances > 0:
                result = equal_no_instances + 1
                remaining_instances -= 1
            else:
                result = equal_no_instances
            instances_per_blocks.append(result)

    logger.debug(f"{requested_instances} instances were divided into {instances_per_blocks}")

    return instances_per_blocks



def merge_csv(directory, output_file):
    file_names = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                file_names.append(file_path)

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        for index, filename in enumerate(file_names):
            with open(filename, 'r') as infile:
                reader = csv.reader(infile)

                if index != 0:
                    next(reader)

                for row in reader:
                    writer.writerow(row)
    
    print('Combined report successfully created')




