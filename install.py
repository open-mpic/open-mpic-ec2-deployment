#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import json
import pprint

import get_ips
import ssh_utils
import time


def parse_args(raw_args):
    parser = argparse.ArgumentParser()
    dirname = os.path.dirname(os.path.realpath(__file__))

    parser.add_argument("-t", "--tf_state",
                        default=f"{dirname}/open-tofu/terraform.tfstate")
    parser.add_argument("-i", "--identity_file",
                        default=f"{dirname}/keys/aws.pem")
    parser.add_argument("-t", "--tmp_dir",
                        default=f"{dirname}/tmp")
    return parser.parse_args(raw_args)




# Main function. Optional raw_args array for specifying command line arguments in calls from other python scripts. If raw_args=none, argparse will get the arguments from the command line.
def main(raw_args=None):
    args = parse_args(raw_args)

    remotes = get_ips.extract_ips(args.tf_state)
    ls_results = ssh_utils.run_cmd_at_remotes(remotes.values(), args.identity_file, "ls")
    startup_script_complete = False
    while not startup_script_complete:
        all_nodes_startup_script_done = True
        for ls_result in ls_results.values():
            if "done.text" not in ls_result:
                all_nodes_startup_script_done = False
                break
        if all_nodes_startup_script_done:
            startup_script_complete = True
            break
        print("Startup script not done... Sleeping 5 sec.")
        time.sleep(5)

    if not os.path.isdir(args.tmp_dir):
        os.mkdir(args.tmp_dir)
    



# Invoke this script after provisioning via open-tofu to print the API's url.


# Main module init for direct invocation. 
if __name__ == '__main__':
    main()
