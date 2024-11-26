
locals {

  ssh_pub_key = file("../keys/aws.pem.pub")
  aws_user_data = <<EOF
#!/bin/bash

echo "Copying the SSH Key to the server"

echo -e "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDiCDkRC+yyu80WDE2fimA7ilXEOkNELRjhJGhMfcHmd3I3C7cBow4pkJjhJrtiglcBHNuEAXuKZpTeogE/jdIEAnBY8MKyR9vqpbK4WllYN2zb6A043XMaF4JKIg77xZVXdl8i+AVsDUeI+zJN1gO8xL38pJ+XCdgxywwjjqesOSDYX/tjWz+g+HhkhjUOa6PWdSyG51Dt97KpP3S2ReH6A9prVJ9CbD/SOH5wc1kRMt9Odzul396x1lMww9xLfT2rgtm+RaLpccFU1N3pYQ7V0o/S8azKfUVdd1eu/YnyUCFrRovP7L5P3NCUHO8RHErp8HOmGznKq8LbIrCwmdSdDAu53aMPFkUiOP3GozsQkyHGeyGXnnLiA87oY1/G9k9f4uGGEauwrfrqWRHNCWAhASiHC69EIn3/d+vZffYJ4NKVC9bJrbCw/8d9GsGw9BD6qn2Lrv23Zpt+fNNA0Mey6wzso8CKuAOQi29i62gEr7Trg21gKo+n6IzXWMaqdyNAYJWz0P4CtAwmh1MEQNnwTphQOLGh1BznL//EvXuu7Rs+pVw1xCh49K3MRlXvEytggpw90UcqiuFpkG0ndf2gUl29JfKJUlBJxmReZcCCI0xcSZKcZNb/aY9q0KE6heESu//Raj2yy1Upc6TkDSCBOMiOTBrl1OlKvz1mibuakQ== henry@MacBook-Pro-11.local" >> /home/ubuntu/.ssh/authorized_keys


apt update
apt install -y git
git clone https://github.com/birgelee/k8-install-scripts.git
cd k8-install-scripts
./install-master.sh >> /home/ubuntu/setup-output.txt

EOF

aws_user_data_template = templatefile(
               "./startup.tftpl",
               {
                 config = {
                   "x"   = "y"
                   "foo" = "bar"
                   "key" = "value"
                 }
               }
              )


}

resource "aws_security_group" "ingress-standard-us-east-2" {
    provider = aws.us-east-2
    name = "allow-all-sg"
    ingress {
        cidr_blocks = [
            "0.0.0.0/0"
        ]
        // TODO: open only kubernetes ports
        from_port = 0
        to_port = 0
        protocol = "-1"
        //from_port = 22
        //to_port = 22
        //protocol = "tcp"
    }// Terraform removes the default rule
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
 }


resource "aws_security_group" "ingress-standard-us-west-2" {
    provider = aws.us-west-2
    name = "allow-all-sg"
    ingress {
        cidr_blocks = [
            "0.0.0.0/0"
        ]
        // TODO: open only kubernetes ports
        from_port = 0
        to_port = 0
        protocol = "-1"
        //from_port = 22
        //to_port = 22
        //protocol = "tcp"
    }// Terraform removes the default rule
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
 }



resource "aws_instance" "worker_us_east_2" {
  ami           = "ami-0f2c72ffadd336b5c"
  instance_type = "t3.medium"
  user_data     = local.aws_user_data_template
  provider = aws.us-east-2
  security_groups = ["${aws_security_group.ingress-standard-us-east-2.name}"]
  tags = {
    Name = "USEast2"
  }
}


resource "aws_instance" "worker_us_west_2" {
  ami           = "ami-04c7330a29e61bbca"
  instance_type = "t3.medium"
  user_data     = local.aws_user_data_template
  provider = aws.us-west-2
  security_groups = ["${aws_security_group.ingress-standard-us-west-2.name}"]
  tags = {
    Name = "USWest2"
  }
}
