

from app import grafana_api

platforms_ = {
    "grafana" : grafana_api
}

def test_connection(platform, connect_string):

    connector = get_connector(platform)
    if not connector:
        error_msg = "%s not supported" % platform
        ret_val = False
    else:
        ret_val, error_msg = connector.test_connection(connect_string)
    return [ret_val, error_msg]


def visualize(platform, report_name, tables):
    pass


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

