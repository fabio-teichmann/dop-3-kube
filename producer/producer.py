import pika, logging, sys, argparse
from argparse import RawTextHelpFormatter
from time import sleep
import os
from datetime import datetime

if __name__ == '__main__':
    examples = sys.argv[0] + " -p 5672 -s rabbitmq -m 'Hello' "
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                 description='Run producer.py',
                                 epilog=examples)
    parser.add_argument('-p', '--port', action='store', dest='port', help='The port to listen on.')
    parser.add_argument('-s', '--server', action='store', dest='server', help='The RabbitMQ server.')
    parser.add_argument('-m', '--message', action='store', dest='message', help='The message to send', required=False, default='Hello')
    parser.add_argument('-r', '--repeat', action='store', dest='repeat', help='Number of times to repeat the message', required=False, default='30')

    args = parser.parse_args()
    if args.port == None:
        print "Missing required argument: -p/--port"
        sys.exit(1)
    if args.server == None:
        print "Missing required argument: -s/--server"
        sys.exit(1)

    # sleep a few seconds to allow RabbitMQ server to come up
    sleep(5)

    logging.basicConfig(level=logging.INFO)
    LOG = logging.getLogger(__name__)
    # Retrieve Base64-encoded username and password from environment variables
    username = os.getenv('RABBITMQ_USER')
    password = os.getenv('RABBITMQ_PASS')
    print username, password
    # Create RabbitMQ connection with decoded credentials
    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(args.server,
                                           int(args.port),
                                           '/',
                                           credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    q = channel.queue_declare('pc')
    q_name = q.method.queue

    # Turn on delivery confirmations
    channel.confirm_delivery()

    for i in range(0, int(args.repeat)):
        if channel.basic_publish('', q_name, args.message):
            LOG.info('{} : Message has been delivered'.format(datetime.now()))
        else:
            LOG.warning('{} : Message NOT delivered'.format(datetime.now()))

        sleep(2)

    connection.close()