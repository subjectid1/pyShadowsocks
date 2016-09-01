#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#

import resource


def get_resource_usage_report():
    r = resource.getrusage(0)

    key_to_description = {
        "ru_utime": "time in user mode (float)",
        "ru_stime": "time in system mode (float)",
        "ru_maxrss": "maximum resident set size",
        "ru_ixrss": "shared memory size",
        "ru_idrss": "unshared memory size",
        "ru_isrss": "unshared stack size",
        "ru_minflt": "page faults not requiring I/O",
        "ru_majflt": "page faults requiring I/O",
        "ru_nswap": "number of swap outs",
        "ru_inblock": "block input operations",
        "ru_oublock": "block output operations",
        "ru_msgsnd": "messages sent",
        "ru_msgrcv": "messages received",
        "ru_nsignals": "signals received",
        "ru_nvcsw": "voluntary context switches",
        "ru_nivcsw": "involuntary context switches",
    }

    return dict([(v, getattr(r, k)) for k, v in key_to_description.items()])


def set_open_file_limit_up_to(limit=65536):
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    limit = max(soft, limit)
    limit = min(limit, hard)

    while limit > soft:
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (limit, hard))
        except ValueError:
            limit -= 256

    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    return (soft, hard)


if __name__ == '__main__':
    print(set_open_file_limit_up_to())
