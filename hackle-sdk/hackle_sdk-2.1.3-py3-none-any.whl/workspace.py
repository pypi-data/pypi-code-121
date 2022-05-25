import json

from hackle.entities import *


class Workspace(object):
    def __init__(self, data):
        json_data = json.loads(data)

        self.bucket_id_map = self._bucket_id_map(json_data.get('buckets', []))
        self.experiment_key_map = self._experiment_key_map('AB_TEST', json_data.get('experiments', []))
        self.feature_flag_key_map = self._experiment_key_map('FEATURE_FLAG', json_data.get('featureFlags', []))
        self.event_type_key_map = self._event_type_key_map(json_data.get('events', []))

    def get_experiment_or_none(self, experiment_key):
        return self.experiment_key_map.get(experiment_key)

    def get_feature_flag_or_none(self, feature_key):
        return self.feature_flag_key_map.get(feature_key)

    def get_bucket_or_none(self, bucket_id):
        return self.bucket_id_map.get(bucket_id)

    def get_event_type_or_none(self, event_key):
        event = self.event_type_key_map.get(event_key)

        if event:
            return event
        else:
            return EventType(0, event_key)

    @staticmethod
    def _bucket_id_map(buckets_data):
        bucket_id_map = {}
        for bucket_data in buckets_data:
            slots = []

            for slot_data in bucket_data['slots']:
                slots.append(
                    Slot(
                        start_inclusive=slot_data['startInclusive'],
                        end_exclusive=slot_data['endExclusive'],
                        variation_id=slot_data['variationId']
                    )
                )

            bucket_id_map[bucket_data['id']] = Bucket(
                seed=bucket_data['seed'],
                slot_size=bucket_data['slotSize'],
                slots=slots
            )
        return bucket_id_map

    @staticmethod
    def _experiment_key_map(experiment_type, experiments_data):
        experiment_key_map = {}
        for experiment_data in experiments_data:
            experiment = Workspace._experiment(experiment_type, experiment_data)
            if experiment:
                experiment_key_map[experiment_data['key']] = experiment
        return experiment_key_map

    @staticmethod
    def _experiment(type, experiment_data):
        variations = []
        for variation_data in experiment_data['variations']:
            variation = Variation(
                id=variation_data['id'],
                key=variation_data['key'],
                is_dropped=variation_data['status'] == 'DROPPED'
            )
            variations.append(variation)

        execution_data = experiment_data['execution']

        user_overrides = {}
        for override_data in execution_data['userOverrides']:
            user_overrides[override_data['userId']] = override_data['variationId']

        status = execution_data['status']
        if status == 'READY':
            return DraftExperiment(
                id=experiment_data['id'],
                key=experiment_data['key'],
                type=type,
                variations=variations,
                user_overrides=user_overrides
            )
        elif status == 'RUNNING':
            return RunningExperiment(
                id=experiment_data['id'],
                key=experiment_data['key'],
                type=type,
                variations=variations,
                user_overrides=user_overrides,
                target_audiences=Workspace._targets(execution_data.get('targetAudiences', [])),
                target_rules=Workspace._target_rules(execution_data.get('targetRules', [])),
                default_rule=Workspace._target_action(execution_data['defaultRule'])
            )
        elif status == 'PAUSED':
            return PausedExperiment(
                id=experiment_data['id'],
                key=experiment_data['key'],
                type=type,
                variations=variations,
                user_overrides=user_overrides
            )
        elif status == 'STOPPED':
            return CompletedExperiment(
                id=experiment_data['id'],
                key=experiment_data['key'],
                type=type,
                variations=variations,
                user_overrides=user_overrides,
                winner_variation_id=experiment_data.get('winnerVariationId')
            )

        return None

    @staticmethod
    def _target(target_data):
        conditions = []

        for condition_data in target_data['conditions']:
            condition = TargetCondition(
                key=TargetKey(
                    type=condition_data['key']['type'],
                    name=condition_data['key']['name']
                ),
                match=TargetMatch(
                    type=condition_data['match']['type'],
                    operator=condition_data['match']['operator'],
                    value_type=condition_data['match']['valueType'],
                    values=condition_data['match']['values']
                )
            )
            conditions.append(condition)

        return Target(conditions)

    @staticmethod
    def _target_action(target_action_data):
        return TargetAction(
            type=target_action_data['type'],
            variation_id=target_action_data.get('variationId'),
            bucket_id=target_action_data.get('bucketId')
        )

    @staticmethod
    def _target_rule(target_rule_data):
        return TargetRule(
            target=Workspace._target(target_rule_data['target']),
            action=Workspace._target_action(target_rule_data['action'])
        )

    @staticmethod
    def _targets(targets_data):
        targets = []
        for target_data in targets_data:
            target = Workspace._target(target_data)
            targets.append(target)
        return targets

    @staticmethod
    def _target_rules(target_rules_data):
        target_rules = []
        for target_rule_data in target_rules_data:
            target_rule = Workspace._target_rule(target_rule_data)
            target_rules.append(target_rule)
        return target_rules

    @staticmethod
    def _event_type_key_map(event_types_data):
        event_type_key_map = {}
        for event_type_data in event_types_data:
            event_type_key_map[str(event_type_data['key'])] = EventType(event_type_data['id'],
                                                                        event_type_data['key'])
        return event_type_key_map
