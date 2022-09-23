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


def orchestrator_function(context: df.DurableOrchestrationContext):
    payload = yield context.call_activity("DurableActivityGetGroups","test")
    logging.info(type(payload))
    parallel_tasks = [ context.call_activity("DurableActivityGetUnits", b) for b in payload ]
    outputs = yield context.task_all(parallel_tasks)
   #added to save custom fields to client table as a look up
    parallel_customfield_tasks = [ context.call_activity("DurableActivityAddCustomFieldtoMaster", b) for b in payload ]
    cf_outputs = yield context.task_all(parallel_customfield_tasks)
    parallel_tasks2 = [ context.call_activity("DurableActivityAddAssetDetails", b) for b in outputs ]
    outputs2 = yield context.task_all(parallel_tasks2)
    #added to get custom fields to each asset
    parallel_tasks3 = [ context.call_activity("DurableActivityAddCustomFieldDetails", b) for b in outputs ]
    outputs3 = yield context.task_all(parallel_tasks3)
    return [payload, outputs, outputs2]

main = df.Orchestrator.create(orchestrator_function)