"""This file is only used for deployment as an AWS Lambda function.
You can delete this file if you are deploying the AI interviewer application on your own dedicated server."""

import json
from core.logic import (
    next_question, 
    retrieve_sessions, 
    transcribe
)

def handler(event, context):
    """This function processes requests to the AWS Lambda function for conducting AI-led interviewers.

    To make API calls to this Lambda function, you need to know the public endpoint (an URL).
    This endpoint is generated when you deploy the Lambda function using the "aws_deploy.sh" script and shown in the output.
    The endpoint always has the following structure:
        
        https://<SOME_STRING>.execute-api.<YOUR_SELECTED_REGION>.amazonaws.com/Prod/
    
    For example, it could look like this:
    
        https://u94z55rxvt.execute-api.eu-north-1.amazonaws.com/Prod/

    The lambda function has three main routes (next, transcribe, and retrieve) that can be accessed via POST requests.

    We describe each route below, including how they can be accessed programmatically. If you use our recommendation
    to integrate the AI interviewer into a Qualtrics survey, you can use the HTML and JavaScript code
    that is provided in the folder 'Qualtrics'. This code is already set up to make requests to the Lambda function.
    This might be instructive for understanding how a front-end would interact with the Lambda function.

    NEXT:
        This route returns the next question in the interview if the interview has already started.
        To start an interview, make a request to this route with an empty user message to receive the first question for the interviewee.

        Example request via Python's requests package:
            ```
            body = {
                "route": "next",
                "payload": {
                    "session_id": "847918419",
                    "interview_id": "STOCK_MARKET", 
                    "user_message": "I don't like risky investments"
                }
            }
            response = requests.post(https://u94z55rxvt.execute-api.eu-north-1.amazonaws.com/Prod/, json=body)
            ```
        
        Example JavaScript request:
            ```
            const body = {
                route: "next",
                payload: {
                    session_id: "847918419",
                    interview_id: "STOCK_MARKET",
                    user_message: "I don't like risky investments"
                }
            };
            fetch('https://u94z55rxvt.execute-api.eu-north-1.amazonaws.com/Prod/', {
                method: 'POST',
                body: JSON.stringify(body),
                contentType: 'application/json'
            });
            ```

    TRANSCRIBE:
        This route transcribes an audio file to text. The audio file must be in base64 string format.

        Example request via Python's requests package:
            ```
            body = {
                "route": "transcribe",
                "payload": {
                    "audio": "base64_encoded_audio_string"
                }
            }
            response = requests.post(https://u94z55rxvt.execute-api.eu-north-1.amazonaws.com/Prod/, json=body)
            ```

        Example JavaScript request:
            ```
            const body = {
                route: "transcribe",
                payload: {
                    audio: "base64_encoded_audio_string"
                }
            };
            fetch('https://u94z55rxvt.execute-api.eu-north-1.amazonaws.com/Prod/', {
                method: 'POST',
                body: JSON.stringify(body),
                contentType: 'application/json',
                dataType: 'json'
            });
            ```

    RETRIEVE:
        This route retrieves all stored interviews from the DynamoDB database.

        Example request via Python's requests package:
            ```
            body = {
                "route": "retrieve",
                "payload": {}
            }
            response = requests.post(https://u94z55rxvt.execute-api.eu-north-1.amazonaws.com/Prod/, json=body)
            ```
            
        Example JavaScript request:
            ```
            const body = {
                route: "retrieve",
                payload: {}
            };
            fetch('https://u94z55rxvt.execute-api.eu-north-1.amazonaws.com/Prod/', {
                method: 'POST',
                body: JSON.stringify(body),
                contentType: 'application/json',
                dataType: 'json'
            });
            ```
    """

    response = {
        "statusCode": 200, 
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",            
            "Access-Control-Allow-Methods": "POST"            
        },
    }

    request = json.loads(event.get('body', '{}'))
    payload = request.get('payload', {})
    if request.get('route') == 'transcribe':
        response['body'] = json.dumps(transcribe(payload['audio']))
    elif request.get('route') == 'next':
        response['body'] = json.dumps(
            next_question(
                payload['session_id'], 
                payload['interview_id'], 
                payload.get('user_message')
            )
        )
    elif request.get('route') == 'retrieve':
        response['body'] = json.dumps(retrieve_sessions())
    else:
        raise ValueError("Invalid request. Please try again.")

    return response
