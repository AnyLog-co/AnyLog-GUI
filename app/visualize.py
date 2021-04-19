

from app import grafana_api

platforms_ = {
    "grafana" : grafana_api
}

def test_connection(platform, connect_string):

    connector = get_connector(platform)
    connector.test_connection(connect_string)


def visualize(platform, report_name, tables):
    pass


# --------------------------------------------------------
# Return the platform connector
# --------------------------------------------------------
def  get_connector(platform):
    return  platforms_[platform]

