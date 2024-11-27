#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import json
import pprint


def parse_args(raw_args):
    parser = argparse.ArgumentParser()
    dirname = os.path.dirname(os.path.realpath(__file__))

    parser.add_argument("-t", "--tf_state",
                        default=f"{dirname}/open-tofu/terraform.tfstate")
    parser.add_argument("-s", "--dns_suffix", default="")
    return parser.parse_args(raw_args)


def extract_ips(tf_state_file_path):
    

    instance_data = {}

    with open(tf_state_file_path) as stream:  # load the tf state file
        tfstate = json.load(stream)
        resources = tfstate['resources']
        for resource in resources:
            resource_type = resource['type']
            if resource_type == "aws_instance":
                name = resource['name']
                if not name.startswith("perspective_"):
                    continue
                region = name[12:]
                instance = resource['instances'][0]
                instance_data[instance['attributes']['public_ip']] = {"dns": None, "region": region}
    return instance_data


# Main function. Optional raw_args array for specifying command line arguments in calls from other python scripts. If raw_args=none, argparse will get the arguments from the command line.
def main(raw_args=None):
    args = parse_args(raw_args)  # get the arguments object
    resources = extract_ips(args.tf_state)
    for ip in resources:
        domain_name = ip.replace(".", "-") + "." + args.dns_suffix
        print(f"domain name: {domain_name} IN A {ip}")
    #pprint.pp(extract_ips(args.tf_state))

# Invoke this script after provisioning via open-tofu to print the API's url.


# Main module init for direct invocation. 
if __name__ == '__main__':
    main()
