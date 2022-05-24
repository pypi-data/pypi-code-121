import copy

from typing import Any, Iterable


class UiReconciler:
    COMPONENT_DELTA_TYPE = "UiComponentsDelta"
    MODIFIED_COMPONENTS_KEY = "modifiedComponents"
    CID_KEY = "_cId"
    """
    Reconciles the SAIL UI, based on the different responses passed
    """

    def reconcile_ui(self, old_state: dict, new_state: dict) -> dict:
        """
        In the case where components are simply modified:
            Makes a copy of the old_state, and applies whichever changes are necessary from the new_state

        In the case where a completely new UI is returned:
            Replaces the old state with the new state
        """
        # Update case
        if 'ui' in new_state and new_state['ui'].get('#t') == UiReconciler.COMPONENT_DELTA_TYPE \
                and UiReconciler.MODIFIED_COMPONENTS_KEY in new_state['ui']:
            old_state_copy = copy.deepcopy(old_state)
            # create a map of cIds to new state components
            component_list = new_state['ui'].get(UiReconciler.MODIFIED_COMPONENTS_KEY)
            cid_to_component = {comp[UiReconciler.CID_KEY]: comp for comp in component_list if UiReconciler.CID_KEY in comp}
            self._traverse_and_update_state(old_state_copy, cid_to_component)

            # Pass context forward as well, for stateless mode
            old_state_copy['context'] = new_state['context']
            return old_state_copy
        else:
            # Simply return the new_state, as we are most likely on a new form
            return new_state

    def _traverse_and_update_state(self, state: Any, cid_to_component: dict) -> None:
        """
        Moves through a dict recursively,
        swapping out any components that have been modified with new ones
        """
        is_dict = isinstance(state, dict)
        if is_dict:
            possible_cid = state.get(UiReconciler.CID_KEY)
            if possible_cid and possible_cid in cid_to_component:
                new_component = cid_to_component[possible_cid]
                state.update(new_component)
                return
        if is_dict or isinstance(state, list):
            elems_to_traverse: Iterable = state.values() if is_dict else state
            for elem in elems_to_traverse:
                if isinstance(elem, (list, dict)):
                    self._traverse_and_update_state(elem, cid_to_component)
