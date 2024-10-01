provider "aws"{
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY 
    secret_key = var.AWS_SECRET_KEY
}

data "aws_security_group" "c13-default-sg" {
    id = var.SECURITY_GROUP_ID
}

data "aws_subnet" "c13-public-subnet" {
  id = var.SUBNET_ID
}

data "aws_ecr_image" "dashboard-image"{
    repository_name = "c13-wshao-dashboard"
    image_tag = "latest"
}

data "aws_iam_role" "execution-role" {
  name = "ecsTaskExecutionRole"
}

data "aws_ecs_cluster" "c13-cluster" {
    cluster_name = "c13-ecs-cluster"
}

data  "aws_iam_policy_document" "schedule-trust-policy" {
    statement {
        effect = "Allow"
        principals {
            type        = "Service"
            identifiers = ["scheduler.amazonaws.com"]
}
        actions = ["sts:AssumeRole"]
    }
}
data "aws_iam_policy_document" "schedule-permissions-policy" {
  statement {
    effect = "Allow"
    resources = [aws_lambda_function.short_pipeline.arn, aws_lambda_function.long_pipeline.arn]
    actions = ["lambda:InvokeFunction"]
  }

  statement {
    effect = "Allow"
    resources = ["*"]
    actions = ["iam:PassRole"]
  }

  statement {
    effect = "Allow"
    resources = ["arn:aws:logs:*:*:*"]
    actions = ["logs:CreateLogStream", "logs:PutLogEvents", "logs:CreateLogGroup"]
  }
}

resource "aws_ecs_task_definition" "dashboard_task"{
    family = "c13-wshao-dashboard"
    network_mode = "awsvpc"
    requires_compatibilities = ["FARGATE"]
    execution_role_arn = data.aws_iam_role.execution-role.arn
    cpu = 256
    memory = 512
    container_definitions = jsonencode([{   
        name = "c13-wshao-dashboard"
        image = data.aws_ecr_image.dashboard-image.image_uri
        essential = true
        portMappings = [
            {
                containerPort = 8501
                hostPort = 8501
            }
        ]
        environment =[
            {
                name = "AWS_ACCESS_KEY"
                value = var.AWS_ACCESS_KEY
            },
            {
                name = "AWS_SECRET_ACCESS_KEY"
                value = var.AWS_SECRET_KEY
            },
            {
                name = "BUCKET"
                value = var.BUCKET
            },
            {
                name = "DB_HOST"
                value = var.DB_HOST
            },         
            {
                name = "DB_PORT"
                value = var.DB_PORT
            },            
            {
                name = "DB_NAME"
                value = var.DB_NAME
            },            
            {
                name = "DB_USER"
                value = var.DB_USER
            },            
            {
                name = "DB_PASSWORD"
                value = var.DB_PW
            },            
        ]
    logConfiguration= {
                logDriver= "awslogs"
                options= {
                    awslogs-group= "/ecs/c13-wshao-dashboard"
                    mode= "non-blocking"
                    awslogs-create-group= "true"
                    max-buffer-size= "25m"
                    awslogs-region= "eu-west-2"
                    awslogs-stream-prefix= "ecs"}}
    }])
}

resource "aws_ecs_service" "dashboard_service" {
    name            = "c13-wshao-dashboard-service"
    cluster         = data.aws_ecs_cluster.c13-cluster.id
    task_definition = aws_ecs_task_definition.dashboard_task.arn
    desired_count   = 1
    launch_type     = "FARGATE"

    network_configuration {
        subnets          = [data.aws_subnet.c13-public-subnet.id]
        security_groups  = [data.aws_security_group.c13-default-sg.id]
        assign_public_ip = true
    }
}

resource "aws_iam_role" "schedule-role" {
    name               = "c13-wshao-pipeline-scheduler-role"
    assume_role_policy = data.aws_iam_policy_document.schedule-trust-policy.json
    inline_policy {
      name = "c13-alex-execution-policy"
      policy = data.aws_iam_policy_document.schedule-permissions-policy.json
    } 
}

resource "aws_scheduler_schedule" "minute" {
  name = "c13-wshao-minute-schedule"
  flexible_time_window {
    mode = "OFF"
  }
  schedule_expression = "cron(* * * * ? *)"
  target {
    arn = aws_lambda_function.short_pipeline.arn
    role_arn = aws_iam_role.schedule-role.arn
  }
}

resource "aws_scheduler_schedule" "daily" {
  name = "c13-wshao-daily-schedule"
  flexible_time_window {
    mode = "OFF"
  }
  schedule_expression = "cron(0 0 * * ? *)"
  target {
    arn = aws_lambda_function.long_pipeline.arn
    role_arn = aws_iam_role.schedule-role.arn
  }
}


data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}


resource "aws_lambda_function" "short_pipeline" {
  function_name = "c13-wshao-short-pipeline-lambda"
  package_type  = "Image"
  image_uri     = var.SHORT_IMAGE_URI
  role          = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      DB_HOST           = var.DB_HOST
      DB_PORT           = var.DB_PORT
      DB_NAME           = var.DB_NAME
      DB_USER           = var.DB_USER
      DB_PASSWORD       = var.DB_PW
    }
  }
}

resource "aws_lambda_function" "long_pipeline" {
  function_name = "c13-wshao-long-pipeline-lambda"
  package_type  = "Image"
  image_uri     = var.LONG_IMAGE_URI
  role          = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      DB_HOST     = var.DB_HOST
      DB_PORT     = var.DB_PORT
      DB_NAME     = var.DB_NAME
      DB_USER     = var.DB_USER
      DB_PASSWORD = var.DB_PW
      DB_BUCKET   = var.BUCKET
    }
  }
}
