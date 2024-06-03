import csv
import os

def split_csv(logger, input_csv, instances_private_ips):
    logger.debug('Spliting data file')
    instance_count = len(instances_private_ips)
    try:
        logger.debug(f"Reading file {input_csv}")
        with open(input_csv, 'r') as file:
            total_lines = sum(1 for line in file)
            logger.debug(f"{total_lines} lines in file {input_csv} files")
        split_size = total_lines // instance_count

        input_basename = os.path.splitext(input_csv)[0]
        with open(input_csv, 'r') as file:
            reader = csv.reader(file)
            index = 0
            output_csv = None
            output_writer = None
            line_count = 0

            for row in reader:
                if index < instance_count and line_count % split_size == 0:
                    if output_csv:
                        output_csv.close()
                    output_csv = open(f"{input_basename}_{instances_private_ips[index]}.csv", 'w', newline='')
                    output_writer = csv.writer(output_csv)
                    index += 1
                output_writer.writerow(row)
                line_count += 1

        if output_csv:
            output_csv.close()

    except ZeroDivisionError:
        with open(input_csv, 'r') as file:
            total_lines = sum(1 for line in file)
            logger.error(f"You have {total_lines} api tokens but created {instance_count} instances")
            logger.error('Requested instances should be less than api tokens')
    except Exception as err:
        logger.exception(f'[Error]: {err}')

