'''
By using this source code, you acknowledge that this software in source code form remains a confidential information of AnyLog, Inc.,
and you shall not transfer it to any other party without AnyLog, Inc.'s prior written consent. You further acknowledge that all right,
title and interest in and to this source code, and any copies and/or derivatives thereof and all documentation, which describes
and/or composes such source code or any such derivatives, shall remain the sole and exclusive property of AnyLog, Inc.,
and you shall not edit, reverse engineer, copy, emulate, create derivatives of, compile or decompile or otherwise tamper or modify
this source code in any way, or allow others to do so. In the event of any such editing, reverse engineering, copying, emulation,
creation of derivative, compilation, decompilation, tampering or modification of this source code by you, or any of your affiliates (term
to be broadly interpreted) you or your such affiliates shall unconditionally assign and transfer any intellectual property created by any
such non-permitted act to AnyLog, Inc.
'''

from app import grafana_api


def update_report():

    platform_info = {
        "url" : 'http://localhost:3000',
        "token" : 'eyJrIjoiaFYzeHZvbWU0RFFkbmVvS0hyVU1taEY5UmhtVmNONWciLCJuIjoiYW55bG9nIiwiaWQiOjF9',
        "report_name" : 'New_Report',
        "tables_list" : [('Orics', 'ALARMS_DESPLAY_TIME')],
        "base" : ['Base-Report'],
        'base_report' : 'AnyLog_Base'

    }


    url, err_msg = grafana_api.deploy_report(**platform_info)

    print("\n\rExit")
    if url:
        print("\n\r%s" % url)
    if err_msg:
        print("\n\r%s" % err_msg)


    return


def main():
    print("\r\nTest Grafana connector")
    update_report()

if __name__ == "__main__":
    main()
