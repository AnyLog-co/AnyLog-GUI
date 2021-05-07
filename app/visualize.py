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

platforms_ = {
    "grafana" : grafana_api
}

def test_connection(platform, connect_string, token):

    connector = get_connector(platform)
    if not connector:
        error_msg = "%s not supported" % platform
        ret_val = False
    else:
        ret_val, error_msg = connector.test_connection(connect_string, token)
    return [ret_val, error_msg]

# --------------------------------------------------------
# Get the list of Reports (Dashboards) for the named report
# --------------------------------------------------------
def get_reports(platform_name, url, token, directory):
    '''
     The list of reports for the named platform and directory
     '''

    connector = get_connector(platform_name)
    if not connector:
        reports_list = None
        error_msg = "%s not supported" % platform_name
    else:
        reports_list, error_msg = connector.get_reports(url, token, directory)


    return [reports_list, error_msg]

# --------------------------------------------------------
# Get the list of panels for the named report
# --------------------------------------------------------
def get_panels(platform_name, url:str, token:str, report_name:str):
    '''
    The list of panels for the named report in the named platform
    '''

    connector = get_connector(platform_name)
    if not connector:
        panels_list = None
        error_msg = "%s not supported" % platform_name
    else:
        panels_list, error_msg = connector.get_panels(url, token, report_name)

    return [panels_list, error_msg]
# --------------------------------------------------------
# Deploy to create or update an exising report in the platform
# --------------------------------------------------------
def deploy_report(platform_name, **platform_info):

    '''
    Deploy a new report (or update existing report) in the platform
    return:
        url to report
        error message
    '''
    connector = get_connector(platform_name)
    if not connector:
        error_msg = "%s not supported" % platform_name
        url = None
    else:
        url, error_msg = connector.deploy_report(**platform_info)

    return [url, error_msg]


# --------------------------------------------------------
# Provide status on the list of entries at platform_info["projection_list]
# --------------------------------------------------------
def status_report(platform_name, **platform_info):

    connector = get_connector(platform_name)
    if not connector:
        error_msg = "%s not supported" % platform_name
        url_list = None
    else:
        url_list, error_msg = connector.status_report(**platform_info)

    return url_list, error_msg

# --------------------------------------------------------
# Return the platform connector
# --------------------------------------------------------
def  get_connector(platform):

    global platforms_
    
    key = platform.lower()
    
    if key in platforms_:
        connector = platforms_[platform.lower()]
    else:
        connector = None

    return connector






