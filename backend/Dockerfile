# Use the official AWS Lambda Python image
FROM public.ecr.aws/lambda/python:3.10

# Copy requirements and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy your application code
COPY . ${LAMBDA_TASK_ROOT}

# Point AWS Lambda to the Mangum handler you just created
CMD [ "main.handler" ]