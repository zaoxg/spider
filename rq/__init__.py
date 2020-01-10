import pika


credentials = pika.PlainCredentials('zhaoxp', '100798')


# 发送端，生产者
def send_task(queue_name, task):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='47.97.166.98', credentials=credentials))
    channel = connection.channel()
    # 声明一个exchange
    channel.exchange_declare(exchange='messages', exchange_type='direct')
    # 声明queue
    channel.queue_declare(queue=queue_name, durable=True)
    # n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
    channel.queue_bind(exchange='messages',
                       queue=queue_name,
                       routing_key=queue_name)

    channel.basic_publish(exchange='messages',
                          routing_key=queue_name,
                          body=task,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # 使消息持久化
                          )
                          )
    print(" [x] Sent %r" % task)
    connection.close()


# 接收端，消费者
def recv_task(queue_name, callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='47.97.166.98', credentials=credentials))
    channel = connection.channel()
    # 声明一个exchange
    channel.exchange_declare(exchange='messages', exchange_type='direct')
    # 声明queue
    channel.queue_declare(queue=queue_name, durable=True)
    # n RabbitMQ消息永远不能直接发送到队列，它总是需要通过交换。
    channel.queue_bind(exchange='messages',
                       queue=queue_name,
                       routing_key=queue_name)
    channel.basic_consume(callback,
                          queue=queue_name,
                          no_ack=False)
    channel.basic_qos(prefetch_count=1)
    channel.start_consuming()
    print(' [*] Waiting for messages. To exit press CTRL+C')
    # channel.start_consuming()
