import json
import logging

log = logging.getLogger(__name__)

def _build_slot_sequence_dict(slotSequenceJSON):
    """
    Utility method to construct a dictionary of the slot sequence.
    """
    slot_sequence = {}

    if slotSequenceJSON:

        for definition in slotSequenceJSON:
            param = definition['slotParameter']
            key = param['key']
            value = param['value']
            slot_sequence[key] = value

    return slot_sequence

def _build_param_dict(paramGroupsJSON):
    """
    Utility method to collate slot parameters and slot parameter
    groups into a dictionary.
    """
    groups = {}
    for group in paramGroupsJSON:
        name = group['slotParameterGroupName']
        
        params = {}
        for param in group['slotParameters']:
            params[param['key']] = param['value']

        groups[name] = params

    return groups

class Submission:
    """
    This Submission class is associated with the v2 submission structure.

    Submission level functionality is handled through this class. Instances of this
    class are created using the LucoApi.get_submission() or LucoApi.create_submission() methods.
    """

    def __init__(self, slot_id, submission_id, core):
        self.slot_id = slot_id
        self.id = submission_id
        self.core = core
        self.__definitionJSON = None

    # Check if GET /slots/{slot_id}/submissions/{submission_id} has been called to 
    # get the submission JSON object.
    def __check_definition_exists(self):
        if not self.__definitionJSON:
            endpoint = f'/v2/slots/{self.slot_id}/submissions/{self.id}'
            r = self.core.get_request(endpoint)
            r.raise_for_status()
            self.__definitionJSON = r.json()

    # The following @property decorated methods prevent the class from calling the api 
    # to get the submission JSON unless necessary the call hasn't been made already.
    @property
    def type(self):
        self.__check_definition_exists()
        return self.__definitionJSON['slotSequence']['definition']['type']['slotSequenceTypeName']

    @property
    def expected_by(self):
        self.__check_definition_exists()
        return self.__definitionJSON['slot']['expectedBy']

    @property
    def name(self):
        self.__check_definition_exists()
        return _build_slot_sequence_dict(self.__definitionJSON['slotSequence']['definition']['name'])

    @property
    def __param_groups(self):
        self.__check_definition_exists()
        return _build_param_dict(self.__definitionJSON['slotSequence']['parameters']['slotParameterGroups'])

    def params(self, group=None, key=None):
        """
        Search for slot parameters.

        Args:
        - group (str) : Parameter group to return
        - key (str) : Key within group to return the value of

        Returns:
        - result (dict or str)
        """
        if group:
            groupName = self.__param_groups[group]

            if key:
                return groupName[key]
            else:
                return groupName
        else:
            return self.__param_groups

    def get_metrics(self, stages=None, metrics=None):
        """
        Retrieve metrics
        
        Filter by stage and metric by passing strings or lists of strings

        Args:
            stages (string)
            metrics (string)

        Returns:
            metrics (dict)
        """
        endpoint = f'/slots/{self.slot_id}/submissions/{self.id}/metrics'

        payload = {}

        # Ensure the parameters are only lists if they contain multiple values
        for param in [stages, metrics]:
            if isinstance(param, list) and len(param) == 1:
                param = param[0]

        # Define payload
        if stages:
            payload['stages'] = stages
        if metrics:
            payload['metrics'] = metrics

        r = self.core.get_request(endpoint, params=payload)
        r.raise_for_status()

        metrics = r.json()['slotSubmissionMetrics']

        if len(metrics) == 1:
            metrics = metrics[0]

        return metrics

    def get_quality(self):
        """
        Retrieve quality results
        
        Returns:
            quality (dict)
        """
        endpoint = f'/slots/{self.slot_id}/submissions/{self.id}/quality'

        r = self.core.get_request(endpoint)
        r.raise_for_status()
        return r.json()

    def submit_run_environment(self, stage=None, run_environments=None):
        """
        Submit run environment details

        Args:
            stage (string) : Optional
            run_environments (dict or list of dicts) : Required

        Returns:
            response status (Bool) : Boolen success or failure       
        """
        endpoint = f'/slots/{self.slot_id}/submissions/{self.id}/runenvironment'

        if isinstance(run_environments, dict):
            run_environments = [run_environments]

        payload = {'stage': stage,
                   'runData': run_environments}

        header = {'content-type': 'application/json-patch+json'}
        r = self.core.post_request(endpoint, additionalHeaders=header, data=json.dumps(payload))
        r.raise_for_status()
        
        self.run_environments = run_environments

        return r.ok

    def submit_metrics(self, stage=None, runId=None, metric=None, value=None, metrics=None):
        """
        Submit metrics

        metrics : takes a dictionary of Metric:Value pairs.

        If only submitting one metric, you can use metric='metric' and value='value'
        """
        endpoint = f'/v2/slots/{self.slot_id}/submissions/{self.id}/metrics'

        if metric and value:
            metrics_list = [{"metric": metric,
                             "value": value}]
                        
        elif metrics:
            metrics_list = []
            for k, v in metrics.items():
                metrics_list.append({"metric": k,
                                     "value": v})

        payload = {'stage': stage,
                   'metrics': metrics_list}

        header = {'content-type': 'application/json-patch+json'}
        r = self.core.post_request(endpoint, additionalHeaders=header, data=json.dumps(payload))

        r.raise_for_status()
        return r.ok

    def submit_quality(self, stage=None, runId=None, tool=None, results=None, dataset=None, action=None):
        """
        Submit metrics
        
        Essential: stage, tool, results and action.
        
        Dataset is optional, runId is no longer stored.
        """
        for param in [tool, results, action]:
            if not param:
                raise Exception('Please provide: tool, results and action')

        endpoint = f'/slots/{self.slot_id}/submissions/{self.id}/quality'

        results = {'stage': stage,
                   'runId': '',
                   'tool': tool,
                   'results': results,
                   'dataSet': dataset,
                   'action': action}

        header = {'content-type': 'application/json-patch+json'}
        r = self.core.post_request(endpoint, additionalHeaders=header, data=json.dumps(results))

        r.raise_for_status()
        return r.ok

    def submit_status(self, status, stage=None, runId=None, type=None, message=None, modified_by=None):
        """
        Submit the status of the Submission

        Args:
            runId       (str)
            status      (str)
            stage       (str)
            type        (str)
            message     (str)
            modified_by (str)

        Returns:
            response status (Bool) : Boolen success or failure
        """
        endpoint = f'/slots/{self.slot_id}/submissions/{self.id}/status'

        data = {'runId': '',
                'status': status,
                'stage' : stage,
                'type': type,
                'message': message,
                'modifiedBy': modified_by}

        header = {'content-type': 'application/json-patch+json'}
        r = self.core.post_request(endpoint, additionalHeaders=header, data=json.dumps(data))

        r.raise_for_status()
        return r.ok

    def submit_completed_status(self):
        """
        Submit a status for a completed submission.

        Equivalent to submit_status('Completed', 'Submission)
        """
        return self.submit_status('Completed', 'Submission')
