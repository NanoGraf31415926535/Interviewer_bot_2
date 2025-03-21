from boto3 import resource
from decimal import Decimal
import logging 


class DynamoDB(object):
    def __init__(self, table_name:str) :
        """ 
        Initialize the Dynamo database table.
        """
        logging.info(f"Setting up DynamoDB for table '{table_name}'")
        self.table = resource('dynamodb').Table(table_name)
        logging.info("DynamoDB table connection established. Should happen only once!")

    def load_remote_session(self, session_id:str) -> list:
        """ Retrieve the interview session data from the database. """
        result = self.table.get_item(Key={'session_id':session_id})
        if result.get('Item'):
            return result['Item']['session']
        logging.warning(f"Can't load session '{session_id}': not started!")
        return {}

    def delete_remote_session(self, session_id:str):
        """ Delete session data from the database. """
        self.table.delete_item(Key={"session_id":session_id})
        logging.info(f"Session '{session_id}' deleted!")

    def update_remote_session(self, session_id:str, session:list):
        """ Update or insert session data in the database. """
        assert 'session_id' in session[-1] and session[-1]['session_id'] == session_id
        self.table.put_item(Item={'session_id':session_id, 'session':session})
        logging.info(f"Session '{session_id}' updated!")

    def retrieve_sessions(self, sessions:list=None) -> list:
        """ 
        Retrieve chat history (list of dicts) for specified sessions
        or *all* sessions if no sessions specified in optional argument.

        Returns
            all_interview_chats: (list) of "long" form data, e.g.
                [
                    {'session_id':101, 'time':0, 'role':'interviewer', 'message':'Hello', ... },
                    {'session_id':101, 'time':1, 'role':'respondent', 'message':'World', ... },
                    ...
                ]
        """
        all_interview_chats = []
        last_eval = None
        while True:
            # Handle multiple chunks with contiguous scan
            resp = self.table.scan(ExclusiveStartKey=last_eval) if last_eval else self.table.scan()
            for item in resp.get('Items', []):
                # Skip keys not specified
                if sessions and not item['session_id'] in sessions: 
                    continue
                # Get JSON serializable data
                session_messages = [dict(map(
                    lambda x: (x[0], int(x[1])) if isinstance(x[1], Decimal) \
                        else x, message.items()
                )) for message in item['session']]
                # Add all messages in current interview session
                all_interview_chats.extend(session_messages)

            if not resp.get('LastEvaluatedKey'): break
            last_eval = resp['LastEvaluatedKey']

        logging.info(f"Retrieved {len(all_interview_chats)} messages!")
        return all_interview_chats
