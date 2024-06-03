from scripts.ec2 import EC2InstanceManager
from scripts.scm import run_ansible
from scripts.data_file import split_csv
from scripts.get_data import read_yaml
from scripts.loadtest import merge_csv
from scripts.validations import validate_input
from scripts.s3 import upload_report_to_s3
from scripts.logger import setup_logger
import argparse

def read_input():

    parser = argparse.ArgumentParser(
        description="Loadtest configuration file"
    )
    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        help="Path to the configuration yaml file",
        required=True
    )
    args = parser.parse_args()
    file_path = args.filename
    config = read_yaml(file_path)
    return config

def main():
    config = read_input()
    log_file_path = config.get('log_file_path', 'loadtest.logs')
    LOGGER = setup_logger(log_file_path)
    validate_input(LOGGER, config)
    response = None
    remote_task_status = 1
    remote_execution_config = {}
    ec2_instances = EC2InstanceManager(LOGGER)
    try:
        response = ec2_instances.create_instances(
            **config
        )
    except Exception as err:
        print(f'[Error]: {err}')

    else:
        if 'jmeter_local_data_dir' in config['loadtest'] and response is not None:
            split_csv(logger=LOGGER, input_csv='data/data.csv', instances_private_ips=[instance['public_ip'] if 'public_ip' in instance else instance['private_ip'] for instance in response[1]])
            print('Data file created successfully')

        remote_execution_config = config.get('remote_execution', {})
        ansible_user = remote_execution_config.get('ssh_user', 'ubuntu')
        ansible_ssh_key_dir = remote_execution_config.get('ssh_key_dir', 'ssh_keys')
        ansible_forks = remote_execution_config.get('parallel_tasks_limit', 10)
        playbook_path = remote_execution_config.get('playbook_file', 'playbook.yaml')

        remote_task_status = run_ansible(
            logger=LOGGER,
            vars=config.get('loadtest', {}),
            running_instances=response[1],
            ansible_user=ansible_user,
            ansible_ssh_key_dir=ansible_ssh_key_dir,
            ansible_forks=ansible_forks,
            playbook_path=playbook_path
        )

    finally:
        if response is not None:
            ec2_instances.terminate_instances(response[0])

    if remote_task_status == 0:

        try:
            lt_report_dir = config['loadtest'].get('output_report_dir', "loadtest_result")
            merge_csv(
                lt_report_dir,
                config['loadtest'].get('combined_csv_report', 'final_loadtest_report.csv')
            )
        except Exception as err:
            print(f'[Error]: {err}')

        else:
            local_playbook_path = remote_execution_config.get('local_playbook_file', 'local_playbook.yaml')
            ansible_run_on_host_machine = run_ansible(
                logger=LOGGER,
                playbook_path=local_playbook_path
            )

            if ansible_run_on_host_machine == 0 and 's3_bucket_name' in config['loadtest']:
                loadtest_name = config['loadtest'].get('name', '')
                final_report_path = config['loadtest'].get('final_report_dir', 'final_report')
                bucket_name = config['loadtest']['s3_bucket_name']
                upload_report_to_s3(LOGGER, final_report_path, bucket_name, loadtest_name)

if __name__ == "__main__":
    main()
