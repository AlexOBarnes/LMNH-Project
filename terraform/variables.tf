variable "AWS_REGION" {
    type = string
    default = "eu-west-2"
}

variable "AWS_ACCESS_KEY"{
    type = string
}

variable "AWS_SECRET_KEY" {
  type = string
}

variable "BUCKET" {
    type = string
}

variable "DB_HOST" {
    type = string
}

variable "DB_PORT" {
    type = string
}

variable "DB_NAME" {
    type = string
}

variable "DB_USER" {
    type = string
}

variable "DB_PW" {
    type = string
}

variable "SECURITY_GROUP_ID" {
    type = string
}

variable "SUBNET_ID" {
    type = string
}

variable "SHORT_IMAGE_URI" {
    type = string
}
variable "LONG_IMAGE_URI" {
    type = string
}

variable "CHECKER_URI" {
    type = string
}
variable "VPC_ID" {
    type = string
}