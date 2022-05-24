from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...extensions import UnknownType
from ...models.aig_generate_input_async_task import AIGGenerateInputAsyncTask
from ...models.aop_process_output_async_task import AOPProcessOutputAsyncTask
from ...models.async_task import AsyncTask
from ...models.autofill_parts_async_task import AutofillPartsAsyncTask
from ...models.autofill_translations_async_task import AutofillTranslationsAsyncTask
from ...models.bulk_create_aa_sequences_async_task import BulkCreateAaSequencesAsyncTask
from ...models.bulk_create_containers_async_task import BulkCreateContainersAsyncTask
from ...models.bulk_create_custom_entities_async_task import BulkCreateCustomEntitiesAsyncTask
from ...models.bulk_create_dna_oligos_async_task import BulkCreateDnaOligosAsyncTask
from ...models.bulk_create_dna_sequences_async_task import BulkCreateDnaSequencesAsyncTask
from ...models.bulk_create_features_async_task import BulkCreateFeaturesAsyncTask
from ...models.bulk_create_rna_oligos_async_task import BulkCreateRnaOligosAsyncTask
from ...models.bulk_create_rna_sequences_async_task import BulkCreateRnaSequencesAsyncTask
from ...models.bulk_register_entities_async_task import BulkRegisterEntitiesAsyncTask
from ...models.bulk_update_aa_sequences_async_task import BulkUpdateAaSequencesAsyncTask
from ...models.bulk_update_containers_async_task import BulkUpdateContainersAsyncTask
from ...models.bulk_update_custom_entities_async_task import BulkUpdateCustomEntitiesAsyncTask
from ...models.bulk_update_dna_oligos_async_task import BulkUpdateDnaOligosAsyncTask
from ...models.bulk_update_dna_sequences_async_task import BulkUpdateDnaSequencesAsyncTask
from ...models.bulk_update_rna_oligos_async_task import BulkUpdateRnaOligosAsyncTask
from ...models.bulk_update_rna_sequences_async_task import BulkUpdateRnaSequencesAsyncTask
from ...models.create_consensus_alignment_async_task import CreateConsensusAlignmentAsyncTask
from ...models.create_template_alignment_async_task import CreateTemplateAlignmentAsyncTask
from ...models.exports_async_task import ExportsAsyncTask
from ...models.not_found_error import NotFoundError
from ...models.transfers_async_task import TransfersAsyncTask
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    task_id: str,
) -> Dict[str, Any]:
    url = "{}/tasks/{task_id}".format(client.base_url, task_id=task_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[
    Union[
        Union[
            AsyncTask,
            CreateTemplateAlignmentAsyncTask,
            CreateConsensusAlignmentAsyncTask,
            BulkCreateDnaSequencesAsyncTask,
            BulkUpdateDnaSequencesAsyncTask,
            BulkCreateRnaSequencesAsyncTask,
            BulkUpdateRnaSequencesAsyncTask,
            AutofillPartsAsyncTask,
            AutofillTranslationsAsyncTask,
            BulkRegisterEntitiesAsyncTask,
            BulkCreateDnaOligosAsyncTask,
            BulkUpdateDnaOligosAsyncTask,
            BulkCreateRnaOligosAsyncTask,
            BulkCreateAaSequencesAsyncTask,
            BulkCreateCustomEntitiesAsyncTask,
            BulkUpdateCustomEntitiesAsyncTask,
            BulkCreateContainersAsyncTask,
            BulkUpdateContainersAsyncTask,
            BulkUpdateAaSequencesAsyncTask,
            BulkUpdateRnaOligosAsyncTask,
            TransfersAsyncTask,
            AOPProcessOutputAsyncTask,
            AIGGenerateInputAsyncTask,
            ExportsAsyncTask,
            BulkCreateFeaturesAsyncTask,
            UnknownType,
        ],
        NotFoundError,
    ]
]:
    if response.status_code == 200:

        def _parse_response_200(
            data: Union[Dict[str, Any]]
        ) -> Union[
            AsyncTask,
            CreateTemplateAlignmentAsyncTask,
            CreateConsensusAlignmentAsyncTask,
            BulkCreateDnaSequencesAsyncTask,
            BulkUpdateDnaSequencesAsyncTask,
            BulkCreateRnaSequencesAsyncTask,
            BulkUpdateRnaSequencesAsyncTask,
            AutofillPartsAsyncTask,
            AutofillTranslationsAsyncTask,
            BulkRegisterEntitiesAsyncTask,
            BulkCreateDnaOligosAsyncTask,
            BulkUpdateDnaOligosAsyncTask,
            BulkCreateRnaOligosAsyncTask,
            BulkCreateAaSequencesAsyncTask,
            BulkCreateCustomEntitiesAsyncTask,
            BulkUpdateCustomEntitiesAsyncTask,
            BulkCreateContainersAsyncTask,
            BulkUpdateContainersAsyncTask,
            BulkUpdateAaSequencesAsyncTask,
            BulkUpdateRnaOligosAsyncTask,
            TransfersAsyncTask,
            AOPProcessOutputAsyncTask,
            AIGGenerateInputAsyncTask,
            ExportsAsyncTask,
            BulkCreateFeaturesAsyncTask,
            UnknownType,
        ]:
            response_200: Union[
                AsyncTask,
                CreateTemplateAlignmentAsyncTask,
                CreateConsensusAlignmentAsyncTask,
                BulkCreateDnaSequencesAsyncTask,
                BulkUpdateDnaSequencesAsyncTask,
                BulkCreateRnaSequencesAsyncTask,
                BulkUpdateRnaSequencesAsyncTask,
                AutofillPartsAsyncTask,
                AutofillTranslationsAsyncTask,
                BulkRegisterEntitiesAsyncTask,
                BulkCreateDnaOligosAsyncTask,
                BulkUpdateDnaOligosAsyncTask,
                BulkCreateRnaOligosAsyncTask,
                BulkCreateAaSequencesAsyncTask,
                BulkCreateCustomEntitiesAsyncTask,
                BulkUpdateCustomEntitiesAsyncTask,
                BulkCreateContainersAsyncTask,
                BulkUpdateContainersAsyncTask,
                BulkUpdateAaSequencesAsyncTask,
                BulkUpdateRnaOligosAsyncTask,
                TransfersAsyncTask,
                AOPProcessOutputAsyncTask,
                AIGGenerateInputAsyncTask,
                ExportsAsyncTask,
                BulkCreateFeaturesAsyncTask,
                UnknownType,
            ]
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = AsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = CreateTemplateAlignmentAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = CreateConsensusAlignmentAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkCreateDnaSequencesAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkUpdateDnaSequencesAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkCreateRnaSequencesAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkUpdateRnaSequencesAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = AutofillPartsAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = AutofillTranslationsAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkRegisterEntitiesAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkCreateDnaOligosAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkUpdateDnaOligosAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkCreateRnaOligosAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkCreateAaSequencesAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkCreateCustomEntitiesAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkUpdateCustomEntitiesAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkCreateContainersAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkUpdateContainersAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkUpdateAaSequencesAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkUpdateRnaOligosAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = TransfersAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = AOPProcessOutputAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = AIGGenerateInputAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = ExportsAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200 = BulkCreateFeaturesAsyncTask.from_dict(data)

                return response_200
            except:  # noqa: E722
                pass
            return UnknownType(data)

        response_200 = _parse_response_200(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[
    Union[
        Union[
            AsyncTask,
            CreateTemplateAlignmentAsyncTask,
            CreateConsensusAlignmentAsyncTask,
            BulkCreateDnaSequencesAsyncTask,
            BulkUpdateDnaSequencesAsyncTask,
            BulkCreateRnaSequencesAsyncTask,
            BulkUpdateRnaSequencesAsyncTask,
            AutofillPartsAsyncTask,
            AutofillTranslationsAsyncTask,
            BulkRegisterEntitiesAsyncTask,
            BulkCreateDnaOligosAsyncTask,
            BulkUpdateDnaOligosAsyncTask,
            BulkCreateRnaOligosAsyncTask,
            BulkCreateAaSequencesAsyncTask,
            BulkCreateCustomEntitiesAsyncTask,
            BulkUpdateCustomEntitiesAsyncTask,
            BulkCreateContainersAsyncTask,
            BulkUpdateContainersAsyncTask,
            BulkUpdateAaSequencesAsyncTask,
            BulkUpdateRnaOligosAsyncTask,
            TransfersAsyncTask,
            AOPProcessOutputAsyncTask,
            AIGGenerateInputAsyncTask,
            ExportsAsyncTask,
            BulkCreateFeaturesAsyncTask,
            UnknownType,
        ],
        NotFoundError,
    ]
]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    task_id: str,
) -> Response[
    Union[
        Union[
            AsyncTask,
            CreateTemplateAlignmentAsyncTask,
            CreateConsensusAlignmentAsyncTask,
            BulkCreateDnaSequencesAsyncTask,
            BulkUpdateDnaSequencesAsyncTask,
            BulkCreateRnaSequencesAsyncTask,
            BulkUpdateRnaSequencesAsyncTask,
            AutofillPartsAsyncTask,
            AutofillTranslationsAsyncTask,
            BulkRegisterEntitiesAsyncTask,
            BulkCreateDnaOligosAsyncTask,
            BulkUpdateDnaOligosAsyncTask,
            BulkCreateRnaOligosAsyncTask,
            BulkCreateAaSequencesAsyncTask,
            BulkCreateCustomEntitiesAsyncTask,
            BulkUpdateCustomEntitiesAsyncTask,
            BulkCreateContainersAsyncTask,
            BulkUpdateContainersAsyncTask,
            BulkUpdateAaSequencesAsyncTask,
            BulkUpdateRnaOligosAsyncTask,
            TransfersAsyncTask,
            AOPProcessOutputAsyncTask,
            AIGGenerateInputAsyncTask,
            ExportsAsyncTask,
            BulkCreateFeaturesAsyncTask,
            UnknownType,
        ],
        NotFoundError,
    ]
]:
    kwargs = _get_kwargs(
        client=client,
        task_id=task_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    task_id: str,
) -> Optional[
    Union[
        Union[
            AsyncTask,
            CreateTemplateAlignmentAsyncTask,
            CreateConsensusAlignmentAsyncTask,
            BulkCreateDnaSequencesAsyncTask,
            BulkUpdateDnaSequencesAsyncTask,
            BulkCreateRnaSequencesAsyncTask,
            BulkUpdateRnaSequencesAsyncTask,
            AutofillPartsAsyncTask,
            AutofillTranslationsAsyncTask,
            BulkRegisterEntitiesAsyncTask,
            BulkCreateDnaOligosAsyncTask,
            BulkUpdateDnaOligosAsyncTask,
            BulkCreateRnaOligosAsyncTask,
            BulkCreateAaSequencesAsyncTask,
            BulkCreateCustomEntitiesAsyncTask,
            BulkUpdateCustomEntitiesAsyncTask,
            BulkCreateContainersAsyncTask,
            BulkUpdateContainersAsyncTask,
            BulkUpdateAaSequencesAsyncTask,
            BulkUpdateRnaOligosAsyncTask,
            TransfersAsyncTask,
            AOPProcessOutputAsyncTask,
            AIGGenerateInputAsyncTask,
            ExportsAsyncTask,
            BulkCreateFeaturesAsyncTask,
            UnknownType,
        ],
        NotFoundError,
    ]
]:
    """ Get a task by id """

    return sync_detailed(
        client=client,
        task_id=task_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    task_id: str,
) -> Response[
    Union[
        Union[
            AsyncTask,
            CreateTemplateAlignmentAsyncTask,
            CreateConsensusAlignmentAsyncTask,
            BulkCreateDnaSequencesAsyncTask,
            BulkUpdateDnaSequencesAsyncTask,
            BulkCreateRnaSequencesAsyncTask,
            BulkUpdateRnaSequencesAsyncTask,
            AutofillPartsAsyncTask,
            AutofillTranslationsAsyncTask,
            BulkRegisterEntitiesAsyncTask,
            BulkCreateDnaOligosAsyncTask,
            BulkUpdateDnaOligosAsyncTask,
            BulkCreateRnaOligosAsyncTask,
            BulkCreateAaSequencesAsyncTask,
            BulkCreateCustomEntitiesAsyncTask,
            BulkUpdateCustomEntitiesAsyncTask,
            BulkCreateContainersAsyncTask,
            BulkUpdateContainersAsyncTask,
            BulkUpdateAaSequencesAsyncTask,
            BulkUpdateRnaOligosAsyncTask,
            TransfersAsyncTask,
            AOPProcessOutputAsyncTask,
            AIGGenerateInputAsyncTask,
            ExportsAsyncTask,
            BulkCreateFeaturesAsyncTask,
            UnknownType,
        ],
        NotFoundError,
    ]
]:
    kwargs = _get_kwargs(
        client=client,
        task_id=task_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    task_id: str,
) -> Optional[
    Union[
        Union[
            AsyncTask,
            CreateTemplateAlignmentAsyncTask,
            CreateConsensusAlignmentAsyncTask,
            BulkCreateDnaSequencesAsyncTask,
            BulkUpdateDnaSequencesAsyncTask,
            BulkCreateRnaSequencesAsyncTask,
            BulkUpdateRnaSequencesAsyncTask,
            AutofillPartsAsyncTask,
            AutofillTranslationsAsyncTask,
            BulkRegisterEntitiesAsyncTask,
            BulkCreateDnaOligosAsyncTask,
            BulkUpdateDnaOligosAsyncTask,
            BulkCreateRnaOligosAsyncTask,
            BulkCreateAaSequencesAsyncTask,
            BulkCreateCustomEntitiesAsyncTask,
            BulkUpdateCustomEntitiesAsyncTask,
            BulkCreateContainersAsyncTask,
            BulkUpdateContainersAsyncTask,
            BulkUpdateAaSequencesAsyncTask,
            BulkUpdateRnaOligosAsyncTask,
            TransfersAsyncTask,
            AOPProcessOutputAsyncTask,
            AIGGenerateInputAsyncTask,
            ExportsAsyncTask,
            BulkCreateFeaturesAsyncTask,
            UnknownType,
        ],
        NotFoundError,
    ]
]:
    """ Get a task by id """

    return (
        await asyncio_detailed(
            client=client,
            task_id=task_id,
        )
    ).parsed
