import subprocess
import yaml


def ansible_inventory(logger, running_instances, ansible_user, ansible_ssh_key_dir, ansible_port=22):
    logger.debug("Creating ansible inventory file")
    with open('inventory', 'w') as file:
        file.write('[webservers] \n')
        for instance in running_instances:

            if 'public_ip' in instance:
                ansible_host = instance['public_ip']
            else:
                ansible_host = instance['private_ip']

            file.write(f"{ansible_host} ansible_user={ansible_user} ansible_ssh_private_key_file={ansible_ssh_key_dir}/{instance['key_name']}.pem ansible_port={ansible_port}\n")
    print(f"Ansible inventory file is created.")
    logger.info(f"Ansible inventory file is created.")

def ansible_vars(logger, **kwargs):
    vars = kwargs
    yaml_vars = yaml.dump(vars)
    logger.debug(f"Ansible vars: {vars}")
    logger.debug("Creating ansible variables file")
    with open('vars_file.yaml', 'w') as file:
        file.write(yaml_vars)

def run_ansible_playbook(logger, playbook_path, inventory_path, ansible_forks):
    command = ["ansible-playbook", playbook_path, "-i", inventory_path, f'--forks={ansible_forks}']
    logger.debug(f"Ansible command: {command}")
    try:
        result = subprocess.run(command, check=True, stderr=subprocess.PIPE, universal_newlines=True)

        print("Ansible playbook executed successfully.")
        logger.info("Ansible playbook executed successfully.")

        return result.returncode

    except subprocess.CalledProcessError as e:
        logger.exception(f"Error executing Ansible playbook: {e}")

def run_ansible(
        playbook_path,
        logger,
        vars=None,
        ansible_user=None,
        ansible_ssh_key_dir=None,
        ansible_forks=5,
        running_instances=None,
        ansible_port=22
    ):
    try:
        if ansible_user != None and running_instances != None:
            ansible_inventory(logger, running_instances, ansible_user, ansible_ssh_key_dir, ansible_port)

        if vars != None:
            ansible_vars(logger, **vars)

        return_status = run_ansible_playbook(logger, playbook_path, 'inventory', ansible_forks)
        return return_status

    except KeyboardInterrupt as err:
        logger.exception(f"Execution interrupted by user: {err}")
        return 1

    except Exception as err:
        logger.exception(f'[Error]: {err}')
        return 1
