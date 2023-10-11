import json
import threading

import pika

from constants import RABBIT_HOST, LLM_UPDATE_QUEUE, LLM_STATUS_QUEUE, BLOG_RSS, BLOG_LINKS_REQUEST, BLOG_LINKS_REPLY, \
    PROMPT_QUEUE, LLM_REPLY_QUEUE
from persistence import persist_documents
from privateGPT import PrivateGPT
from utils import parse_blog_document

is_updating_data = False


def publish_message(message: str, queue: str):
    bytes_msg = message.encode('utf-8')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(exchange='', routing_key=queue, body=bytes_msg)
    print(f"message {message} is sent to {queue}")
    channel.close()
    connection.close()


def consume_message(target_queue: str, target_callback: ()):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=target_queue)
    channel.basic_consume(queue=target_queue, on_message_callback=target_callback, auto_ack=True)
    channel.start_consuming()


# listen to data update request.
# if a signal is captured, then it will send signal to processors
# it will wait for processors' reply and data
# ingest the data and keep updating the status to client
# channels: LLM_UPDATE_QUEUE & LLM_STATUS_QUEUE
def start_listen_data_update_request():
    print('Listening to data-update request...')
    consume_message(LLM_UPDATE_QUEUE, data_update_request_receiver)


def data_update_request_receiver(channel, method, properties, body):
    global is_updating_data
    if is_updating_data:
        print("llm engine is still busy persisting data")
        return

    is_updating_data = True
    request = body.decode('utf-8')
    print(f"data-update request: {request}")
    publish_message('start', LLM_STATUS_QUEUE)
    blog_links_thread = threading.Thread(target=start_links_request)
    blog_links_thread.start()
    blog_links_thread.join()


# send data update status to client
# send data request to blog rss processor
# listening to reply
def start_links_request():
    publish_message('get-rss', LLM_STATUS_QUEUE)
    publish_message(BLOG_RSS, BLOG_LINKS_REQUEST)
    print('Listening to blog processor reply...')
    consume_message(BLOG_LINKS_REPLY, links_receiver)


def links_receiver(channel, method, properties, body):
    print(f"Received processor: {channel}")
    bytes_to_string = body.decode('utf-8')
    links = json.loads(bytes_to_string)
    print(f"Links data received: {len(links)}")
    channel.stop_consuming()

    publish_message('parse blog documents', LLM_STATUS_QUEUE)
    docs = parse_blog_document(links)

    publish_message('saving the docs', LLM_STATUS_QUEUE)
    persist_documents(docs)

    publish_message('finish', LLM_STATUS_QUEUE)

    global is_updating_data
    is_updating_data = False


def start_listen_prompt():
    # need to add broker credentials
    print('Listening to prompt. To exit press CTRL+C')
    consume_message(PROMPT_QUEUE, prompt_receiver)


def prompt_receiver(channel, method, properties, body):
    prompt = body.decode('utf-8')
    print(f"Prompt received: {prompt}")
    reply = PrivateGPT().qa_prompt(prompt)
    publish_message(reply, LLM_REPLY_QUEUE)
    print('LLM reply sent')
