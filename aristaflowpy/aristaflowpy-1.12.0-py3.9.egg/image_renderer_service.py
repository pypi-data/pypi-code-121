# AristaFlow REST Libraries
from af_process_image_renderer import RenderOptions
from af_process_image_renderer.api.process_image_renderer_api import ProcessImageRendererApi
from aristaflow.abstract_service import AbstractService


class ImageRendererService(AbstractService):

    def get_process_image_instance(self, inst_id):
        pir: ProcessImageRendererApi = self._service_provider.get_service(ProcessImageRendererApi)

        return pir.get_instance(inst_id, body=RenderOptions(type='PNG', data_edges_visible=False, data_elements_visible=False,
                                                                              data_flow_lane_visible=False,
                                                                              decision_data_edges_visible=False,
                                                                              decision_data_elements_visible=False,
                                                                              system_data_elements_visible=False,
                                                                              hidden_nodes_visible=False,
                                                                              sync_edges_visible=True,
                                                                              system_data_edges_visible=False,
                                                                              adv_options={"GraphFigureProviderID":
                                                                                           "de.aristaflow.adept2.ui.processvisualisation.widgets.bpmn.BPMNSymbols"}))
