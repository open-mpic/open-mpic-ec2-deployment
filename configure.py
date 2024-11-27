#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import yaml
import secrets
import string


def parse_args(raw_args):
    parser = argparse.ArgumentParser()
    dirname = os.path.dirname(os.path.realpath(__file__))

    parser.add_argument("-c", "--config",
                        default=f"{dirname}/config.yaml")
    parser.add_argument("-r", "--available_regions",
                        default=f"{dirname}/aws-available-regions.yaml")
    parser.add_argument("-m", "--main_tf_template",
                        default=f"{dirname}/open-tofu/main.tf.template")
    parser.add_argument("-a", "--aws_perspective_tf_template",
                        default=f"{dirname}/open-tofu/aws-ec2-perspective.tf.template")
    parser.add_argument("-k", "--api_key_file",
                        default=f"{dirname}/keys/api.key")
    parser.add_argument("-p", "--aws_provider_tf_template",
                        default=f"{dirname}/open-tofu/aws-provider.tf.template")
    parser.add_argument("-d", "--deployment_id_file",
                        default=f"{dirname}/deployment.id")
    parser.add_argument("-i", "--ami_info",
                        default=f"{dirname}/ami-info.txt")
    return parser.parse_args(raw_args)


# Main function. Optional raw_args array for specifying command line arguments in calls from other python scripts. If raw_args=none, argparse will get the arguments from the command line.
def main(raw_args=None):
    # Get the arguments object.
    args = parse_args(raw_args)

    # If the deployment id file does not exist, make a new one.
    if not os.path.isfile(args.deployment_id_file):
        with open(args.deployment_id_file, 'w') as stream:
            deployment_id_to_write = ''.join(secrets.choice(string.digits) for i in range(10))
            stream.write(deployment_id_to_write)
    
    # Read the deployment id.
    deployment_id = 0
    with open(args.deployment_id_file) as stream:
        deployment_id = int(stream.read())

    # Load the config.
    config = {}
    with open(args.config) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(f"Error loading YAML config at {args.config}. Project not configured. Error details: {exec}.")
            exit()
    aws_available_regions = {}
    with open(args.available_regions) as stream:
        try:
            aws_available_regions = yaml.safe_load(stream)['aws-available-regions']
        except yaml.YAMLError as exc:
            print(f"Error loading YAML config at {args.available_regions}. Project not configured. Error details: {exec}.")
            exit()

    # Remove all old files.
    open_tofu_dir = '/'.join(args.aws_perspective_tf_template.split('/')[:-1])
    for file in os.listdir(open_tofu_dir):
        if file.endswith(".generated.tf"):
            os.remove(os.path.join(open_tofu_dir, file))

    regions = config['perspectives']


    with open(args.aws_provider_tf_template) as stream:
        aws_provider_tf = stream.read()
        result_string = ""
        for region in aws_available_regions:
            result_string += aws_provider_tf.replace("{{region}}", region)
            result_string += "\n"
        out_file_name = f"{'.'.join(args.aws_provider_tf_template.split('.')[:-2])}.generated.tf"

        with open(out_file_name, 'w') as out_stream:
            out_stream.write(result_string)

    ami_info_dict = {}
    with open(args.ami_info) as f:
        # File from https://cloud-images.ubuntu.com/locator/ec2/
        for line in f:
            sline = line.strip()
            if sline == "":
                continue
            splitLine = sline.split("\t")
            if len(splitLine) < 5:
                continue
            ami = splitLine[6]

            region = splitLine[0]

            arch = splitLine[3]
            if arch == "amd64":
                ami_info_dict[region] = ami
            #print(f"ami: {ami}, region: {region}")





    # Generate aws-perspective-template.generated.tf based on aws-perspective-template.tf.template.
    with open(args.aws_perspective_tf_template) as stream:
        # Read the template file to a string.
        aws_perspective_tf = stream.read()

        # Iterate through the different regions specified and produce an output file for each region.
        for perspective in config['perspectives']:
            region = perspective

            aws_perspective_tf_region = aws_perspective_tf.replace("{{region}}", region)
            
            # Replace the deployment id.
            aws_perspective_tf_region = aws_perspective_tf_region.replace("{{deployment-id}}", str(deployment_id))
            
            aws_perspective_tf_region = aws_perspective_tf_region.replace("{{ami}}", ami_info_dict[region])

            if not args.aws_perspective_tf_template.endswith(".tf.template"):
                print(f"Error: invalid tf template name: {args.aws_perspective_tf_template}. Make sure all tf template files end in '.tf.template'.")
                exit()
            out_file_name = f"{'.'.join(args.aws_perspective_tf_template.split('.')[:-2])}.{region}.generated.tf"

            with open(out_file_name, 'w') as out_stream:
                out_stream.write(aws_perspective_tf_region)


    # Get API Key
        
    if not os.path.isfile(args.api_key_file):
        with open(args.api_key_file, 'w') as f:
            api_key_generated = ''.join(secrets.choice(string.ascii_letters) for i in range(30))
            f.write(api_key_generated)

    return


        

# Main module init for direct invocation. 
if __name__ == '__main__':
    main()