from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import time
import logging 

def chat_to_string(chat:list, only_topic:int=None, until_topic:int=None) -> str:
    """ Convert messages from chat into one string. """
    topic_history = ""
    for message in chat:
        # If desire specific topic's chat history:
        if only_topic and message['topic_idx'] != only_topic: 
            continue
        if until_topic and message['topic_idx'] == until_topic:
            break
        if message["type"] == "question":
            topic_history += f'Interviewer: "{message['content']}"\n'
        if message["type"] == "answer":
            topic_history += f'Interviewee: "{message['content']}"\n'
    return topic_history.strip()

def fill_prompt_with_interview(template:str, topics:list, history:list, user_message:str=None) -> str:
    """ Fill the prompt template with parameters from current interview. """
    state = history[-1]
    current_topic_idx = min(int(state['topic_idx']), len(topics))
    next_topic_idx = min(current_topic_idx + 1, len(topics))
    current_topic_chat = chat_to_string(history, only_topic=current_topic_idx)
    prompt = template.format(
        topics='\n'.join([topic['topic'] for topic in topics]),
        question=state["content"],
        answer=user_message,
        summary=state['summary'] or chat_to_string(history, until_topic=current_topic_idx),
        current_topic=topics[current_topic_idx - 1]["topic"],
        next_interview_topic=topics[next_topic_idx - 1]["topic"],
        current_topic_history=current_topic_chat
    )
    logging.debug(f"Prompt to GPT:\n{prompt}")
    assert not re.findall(r"\{[^{}]+\}", prompt)
    return prompt 

def execute_queries(query, task_args:dict) -> dict:
    """ 
    Execute queries (concurrently if multiple).

    Args:
        query: function to execute
        task_args: (dict) of arguments for each task's query
    Returns:
        suggestions (dict): {task: output} 
    """
    st = time.time()
    suggestions = {}
    with ThreadPoolExecutor(max_workers=len(task_args)) as executor:
        futures = {
            executor.submit(query, **kwargs): task 
                for task, kwargs in task_args.items()
        }
        for future in as_completed(futures):
            task = futures[future]
            resp = future.result().choices[0].message.content.strip("\n\" '''")
            suggestions[task] = resp

    logging.info("OpenAI query took {:.2f} seconds".format(time.time() - st))
    logging.info(f"OpenAI query returned: {suggestions}")
    return suggestions
