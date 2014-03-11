from flask import Flask, request  # , jsonify, redirect
from flask.ext.restful import Api, Resource, abort  # , reqparse
#from json import loads
import xml.etree.cElementTree as ET
from operator import itemgetter
from threading import Thread

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['FAIL'] = False
api = Api(app)

tasks = {}

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('no server running')
    func()

def set_to_fail():
    app.config['FAIL'] = True

def set_amq(ip):
    app.config['AMQ'] = ip


@app.route('/amq/<string:ip>', methods=['POST'])
def amq(ip):
    set_amq(ip)
    return str(app.config)

@app.route('/fail', methods=['POST'])
def fail():
    set_to_fail()
    return str(app.config)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'shuting down server'



class qtsAPI(Resource):
    """
    """
    def get(self):
        return tasks

    def post(self):
        status = app.config['FAIL']
        request_id = '1'
        if request.data:
            tree = ET.fromstring(request.data)
            command_name = tree.attrib['name']
            task_id = 'task_%d' % (len(tasks) + 1)
#            tasks[task_id] = request.data
            tasks[task_id] = request.data
            if command_name == 'GetTaskStatus':
                message = '''
                        <returnValue>
                            <dateTime>2013-07-09T07:32:40Z</dateTime>
                            <timeStamp>635089519603554687</timeStamp>
                            <success>True</success>
                            <messages />
                            <data>
                                <task>
                                    <taskID>27</taskID>
                                    <taskGUID>786ab22e-df31-44ae-9973-0eb3cd00bb4e</taskGUID>
                                    <status>%s</status>
                                </task>
                            </data>
                        </returnValue>''' % status
            else:
                message = '''
                    <returnValue>
                        <dateTime>2013-07-05T14:39:10Z</dateTime>
                        <timeStamp>635086319503037109</timeStamp>
                        <success>True</success>
                        <messages />
                        <data>
                            <taskGUID>786ab22e-df31-44ae-9973-0eb3cd00bb4e</taskGUID>
                            <taskID>27</taskID>
                            <requestID>%s</requestID>
                            <commandName>%s</commandName>
                            <timeQueued>7/5/2013 4:39:10 PM</timeQueued>
                        </data>
                    </returnValue>''' % (request_id, command_name)

                qts_worker = worker(request.data, status, self.server.amqhostname)
                qts_worker.start()
        else:
            abort(400)
       #        return (request.data + ':' + str(res))

        return message


api.add_resource(qtsAPI, '/')

class worker(Thread):

    WORKING_REPLY = '''
<handleEvent>
  <commandName>%s</commandName>
  <event>
    <dateTime>2013-07-05T08:14:52Z</dateTime>
    <timeStamp>635086088925722656</timeStamp>
    <messages />
    <data>
      <taskGUID>b9f69ae5-c1bf-406c-bf88-8dbaa7034d6c</taskGUID>
      <taskID>25</taskID>
      <requestID>%s</requestID>
      <attemptNumber>1</attemptNumber>
      <maxAttempts>3</maxAttempts>
      <previousStatus>Queued</previousStatus>
      <currentStatus>Working</currentStatus>
      <workerName>PAN</workerName>
      <workerIPAddress>172.16.124.75</workerIPAddress>
    </data>
    <type>statusChange</type>
    <target>
      <machineName />
      <application>QTS</application>
      <instance />
    </target>
  </event>
</handleEvent>
'''
    SUCCESS_REPLY = '''
<handleEvent>
  <commandName>%s</commandName>
  <event>
    <dateTime>2013-07-05T08:14:54Z</dateTime>
    <timeStamp>635086088948925781</timeStamp>
    <messages />
    <data>
      <taskGUID>b9f69ae5-c1bf-406c-bf88-8dbaa7034d6c</taskGUID>
      <taskID>25</taskID>
      <requestID>%s</requestID>
      <attemptNumber>1</attemptNumber>
      <maxAttempts>3</maxAttempts>
      <pluginVersion>3.5.0.8487</pluginVersion>
      <processingTime>00:00:00.269</processingTime>
      <cpuTime>00:00:00</cpuTime>
      <previousStatus>Working</previousStatus>
      <currentStatus>Succeeded</currentStatus>
      <workerName>PAN</workerName>
    </data>
    <type>statusChange</type>
    <target>
      <machineName />
      <application>QTS</application>
      <instance />
    </target>
  </event>
</handleEvent>
    '''

    FAIL_REPLY = '''
<handleEvent>
  <commandName>%s</commandName>
  <event>
    <dateTime>2013-07-05T08:14:54Z</dateTime>
    <timeStamp>635086088948925781</timeStamp>
    <messages />
    <data>
      <taskGUID>b9f69ae5-c1bf-406c-bf88-8dbaa7034d6c</taskGUID>
      <taskID>25</taskID>
      <requestID>%s</requestID>
      <attemptNumber>3</attemptNumber>
      <maxAttempts>3</maxAttempts>
      <currentStatus>Failed</currentStatus>
      <previousStatus>Working</previousStatus>
    </data>
    <type>statusChange</type>
    <target>
      <machineName />
      <application>QTS</application>
      <instance />
    </target>
  </event>
</handleEvent>
    '''

    def __init__(self, xml, fail, amqhostname):
        super(qts, self).__init__()
        self.xml = xml
        self.fail = fail
        self.amqhostname = amqhostname

    def run(self):
        tree = ET.fromstring(self.xml)
        for el in tree.getiterator('requestor'):
            for st in list(el):
                if st.tag == 'requestID':
                    requestId = st.text

        commandname = tree.attrib['name']

        from activemqueue import activemqueue

        q = activemqueue(amqHostname = self.amqhostname)
        #works on the task
        #raw_input("Queued to Working: %s, %s" % (commandname, requestId))
        sleep(5)
        q._send_message_queue(self.WORKING_REPLY % (commandname, requestId), 'qts2jbpm')

        #completes the task
        #raw_input("Working to Succeeded: %s, %s" % (commandname, requestId))
        logging.debug('Sim State: %s' % self.fail)
        sleep(5)
        if self.fail:
            q._send_message_queue(self.FAIL_REPLY % (commandname, requestId), 'qts2jbpm')
        else:
            q._send_message_queue(self.SUCCESS_REPLY % (commandname, requestId), 'qts2jbpm')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8077, debug=True)
