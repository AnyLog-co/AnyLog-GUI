# The following install a docker instance of Grafana: https://grafana.com/docs/grafana/latest/administration/configure-docker/
# default: admin | password 
# user is required to change password when first starting 

docker volume create grafana-data
docker volume create grafana-log 
docker volume create grafana-config

# start grafana
docker run -d -p 3000:3000 --name=grafana -v grafana-data:/var/lib/grafana -v grafana-log:/var/log/grafana -v grafana-config:/etc/grafana -e "GF_INSTALL_PLUGINS=simpod-json-datasource,grafana-worldmap-panel" grafana/grafana


sudo ufw allow 3000



