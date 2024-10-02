provider "aws"{
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY 
    secret_key = var.AWS_SECRET_KEY
}

data "aws_vpc" "c13-vpc" {
  id = var.VPC_ID
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
    resources = [
      aws_sfn_state_machine.plant_state_function.arn,
      aws_lambda_function.long_pipeline.arn
    ]
    actions = [
      "states:StartExecution",
      "lambda:InvokeFunction"
    ]
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


resource "aws_security_group" "dash_security_group" {
  name        = "c13-wshao-dashboard-security-group"
  description = "Security group to allow TCP traffic on port 8501"
  vpc_id      = data.aws_vpc.c13-vpc.id

  ingress {
    description      = "Allow TCP traffic on port 8501"
    from_port        = 8501
    to_port          = 8501
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
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
        security_groups  = [aws_security_group.dash_security_group.id]
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
    arn = aws_sfn_state_machine.plant_state_function.arn
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
      MY_AWS_ACCESS_KEY = var.AWS_ACCESS_KEY
      MY_AWS_SECRET_KEY = var.AWS_SECRET_KEY
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
      MY_AWS_ACCESS_KEY = var.AWS_ACCESS_KEY
      MY_AWS_SECRET_KEY = var.AWS_SECRET_KEY
    }
  }
}

resource "aws_lambda_function" "plant_checker" {
  function_name = "c13-wshao-plant_checker_lambda"
  package_type  = "Image"
  image_uri     = var.CHECKER_URI
  role          = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      DB_HOST     = var.DB_HOST
      DB_PORT     = var.DB_PORT
      DB_NAME     = var.DB_NAME
      DB_USER     = var.DB_USER
      DB_PASSWORD = var.DB_PW
      DB_BUCKET   = var.BUCKET
      MY_AWS_ACCESS_KEY = var.AWS_ACCESS_KEY
      MY_AWS_SECRET_KEY = var.AWS_SECRET_KEY
    }
  }
}

resource "aws_iam_role" "step_function_role" {
  name = "c13-wshao-step-function-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "step_function_policy" {
  name = "c13-wshao-step-function-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "lambda:InvokeFunction"
        Resource = [
          aws_lambda_function.short_pipeline.arn,
          aws_lambda_function.plant_checker.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_step_function_policy" {
  role       = aws_iam_role.step_function_role.name
  policy_arn = aws_iam_policy.step_function_policy.arn
}

resource "aws_sfn_state_machine" "plant_state_function" {
  name     = "c13-wshao-step-function"
  role_arn = aws_iam_role.step_function_role.arn
  definition = jsonencode({
    "Comment": "Step function to invoke short_pipeline and plant_checker Lambdas",
    "StartAt": "InvokeShortPipeline",
    "States": {
      "InvokeShortPipeline": {
        "Type": "Task",
        "Resource": aws_lambda_function.short_pipeline.arn,
        "Next": "InvokePlantChecker"
      },
      "InvokePlantChecker": {
        "Type": "Task",
        "Resource": aws_lambda_function.plant_checker.arn,
        "End": true
      }
    }
  })
}
