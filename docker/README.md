Set of dockerfiles and docker-compose to deploy the GUI

Composed of Grafana and GUI

Grafana
Git clone grafana.ini, plugins, dashboards and data sources into Docker Template directory
Install base Grafana container and add Docker Volume for Grafana.ini, Default Dashboard and Default Data Sources

Flask
Git clone app.py and Python helper files into Flask directory
Install Flask container and configure with Flask directory
