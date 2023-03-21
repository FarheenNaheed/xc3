namespace                  = "yaseen"
region                     = "eu-west-1"
account_id                 = "201635854701"
vpc_cidr_block             = "14.0.0.0/24"
public_subnet_cidr_block   = "14.0.0.0/26"
private_subnet_cidr_block  = "14.0.0.64/26"
allow_traffic              = ["39.46.215.160/32", "202.69.61.0/24"]
ses_email_address          = "yaseen.zafar@xgrid.co"
creator_email              = "yaseen.zafar@xgrid.co"
ssh_key                    = "yaseen-key"
instance_type              = "t2.micro"
total_account_cost_lambda  = "total_account_cost"
total_account_cost_cronjob = "cron(0 0 */2 * ? *)"
prometheus_layer           = "lambda_layers/python.zip"
mysql_layer                = "lambda_layers/layer-mysql-prometheus.zip"
memory_size                = 128
timeout                    = 300
security_group_ingress = {
  "pushgateway" = {
    description = "PushGateway"
    from_port   = 9091
    to_port     = 9091
    protocol    = "tcp"
    cidr_blocks = ["14.0.0.64/26"]
  },
  "prometheus" = {
    description = "Prometheus"
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["14.0.0.64/26"]
  },
  "http" = {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["14.0.0.64/26"]
  },
  "https" = {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["14.0.0.64/26"]
  },
  "grafana" = {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["14.0.0.64/26"]
  }
}