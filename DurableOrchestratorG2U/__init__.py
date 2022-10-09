# This function is not intended to be invoked directly. Instead it will be
# triggered by an HTTP starter function.
# Before running this sample, please:
# - create a Durable activity function (default name is "Hello")
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import json

import azure.functions as func
import azure.durable_functions as df
import itertools

def orchestrator_function(context: df.DurableOrchestrationContext):
    #a data can be passed in this case it is test
    # the first function does the following
    # Input - a text called test is passed - no processing or value
    # processing gets all the clients from the clientstable and sends this onwards
    # Output  - a dump of all columns and rows of the clientTable
    payload = yield context.call_activity("DurableActivityGetGroups","test")
    # now parallel tasks are running on each client
    # input a client detail item from the list is split across
    # processing - each function gets one set of data for a client
    # Output - a collection of apikey, group and units are packed as a list and returned
    # The parallel tasks will now be a list of the collection 
    parallel_tasks = [ context.call_activity("DurableActivityGetUnits", b) for b in payload ]
    outputs = yield context.task_all(parallel_tasks)
    # process to add asset details to the asset database
    # input a client detail item from db as the list is split across
    # Output Each units is added with the master details to asset tables
    parallel_tasks2 = [ context.call_activity("DurableActivityAddAssetDetails", b) for b in outputs ]
    outputs2 = yield context.task_all(parallel_tasks2)
    #added to get custom fields to each asset
    # input a collection of apikey, group and units are packed as a list fanned out
    # Output Each units custom field is added on a custom field table
    parallel_tasks3 = [ context.call_activity("DurableActivityAddCustomFieldDetails", b) for b in outputs ]
    outputs3 = yield context.task_all(parallel_tasks3)
    action_list=[]
    for item in itertools.chain.from_iterable(outputs3):
        action_list.append(item)
    parallel_tasks4 = [ context.call_activity("DurableActivityProcessFile", b) for b in action_list ]
    outputs4 = yield context.task_all(parallel_tasks4)

    return [payload, outputs, outputs2,outputs3,outputs4]

main = df.Orchestrator.create(orchestrator_function)