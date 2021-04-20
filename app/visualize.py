


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


def visualize(platform, report_name, tables):
    pass

# --------------------------------------------------------
# Deploy to create or update an exising report in the platform
# --------------------------------------------------------
def deploy_report(platform_name, connect_string, token, report_name, tables_list):

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
        url, error_msg = connector.deploy_report(connect_string, token, report_name, tables_list)

    return [url, error_msg]


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






