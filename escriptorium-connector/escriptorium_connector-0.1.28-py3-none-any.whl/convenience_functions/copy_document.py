from alive_progress import alive_bar
from colorama import init, Fore, Style

init()
from io import BytesIO
from datetime import datetime
import logging
from typing import List, Generator, NamedTuple, Tuple, Union
from escriptorium_connector import EscriptoriumConnector
from escriptorium_connector.dtos import (
    PostProject,
    PostDocument,
    PostPart,
    GetPart,
    GetAbbreviatedTranscription,
    GetRegionType,
    GetLineType,
)

log_file = "copy_escriptorium_document.log"
logging.basicConfig(filename=log_file, filemode="w", level=logging.DEBUG)


class CopyProgress(NamedTuple):
    main_progress: int
    main_complete_total: int
    sub_progress: int
    sub_complete_total: int
    sub_msg: Union[str, None]
    main_msg: Union[str, None] = "copying documents from source to destination"
    done: bool = False


def copy_documents(
    source_server: EscriptoriumConnector,
    destination_server: EscriptoriumConnector,
    documents: List[int],
    project_slug: str,
    ignore_images: bool = False,
    duplicate: bool = False,
):
    """The simplest way to copy an eScriptorium document.
    It performs the copy without providing any progress
    monitoring. The logfile is still used and provides
    some process messages.

    Args:
        source_server (EscriptoriumConnector): A connection to the eScriptorium
        server that holds the source for the documents are being copied.
        destination_server (EscriptoriumConnector): A connection to the
        eScriptorium server to which the documents are being copied.
        documents (List[int]): A list of the document PKs on the source_server
        that should be copied to the destination_server.
        project_slug (str, optional): Slug for the project on the destination_server 
        ignore_images (bool, optional): Whether or not to copy images from the
        source_server to the destination_server. Defaults to False.
        duplicate (bool, optional): Whether or not the documents are being
        duplicated on the same eScriptorium server. Defaults to False.
    """

    for _ in copy_documents_generator(
        source_server,
        destination_server,
        documents,
        project_slug,
        ignore_images,
        duplicate,
    ):
        pass


def copy_documents_monitored(
    source_server: EscriptoriumConnector,
    destination_server: EscriptoriumConnector,
    documents: List[int],
    project_slug: str,
    ignore_images: bool = False,
    duplicate: bool = False,
):
    """A monitored eScriptorium document copy process.
    It performs the copy and prints to the console
    status reports about the progress of the copy process.
    The progress reporting also works automatically with
    a Jupyter notebook. The logfile is also used and provides
    some process messages.

    Args:
        source_server (EscriptoriumConnector): A connection to the eScriptorium
        server that holds the source for the documents are being copied.
        destination_server (EscriptoriumConnector): A connection to the
        eScriptorium server to which the documents are being copied.
        documents (List[int]): A list of the document PKs on the source_server
        that should be copied to the destination_server.
        project_slug (str, optional): Slug for the project on the destination_server 
        ignore_images (bool, optional): Whether or not to copy images from the
        source_server to the destination_server. Defaults to False.
        duplicate (bool, optional): Whether or not the documents are being
        duplicated on the same eScriptorium server. Defaults to False.
    """
    start_time = datetime.now()
    color_wheel = [
        Fore.LIGHTBLUE_EX,
        Fore.LIGHTCYAN_EX,
        Fore.LIGHTMAGENTA_EX,
        Fore.LIGHTRED_EX,
        Fore.LIGHTYELLOW_EX,
    ]
    color_wheel_idx = 0
    copy_monitor = copy_documents_generator(
        source_server,
        destination_server,
        documents,
        project_slug,
        ignore_images,
        duplicate,
    )
    progress = next(copy_monitor)
    current_submessage = progress.sub_msg
    current_subprocess_total = progress.sub_complete_total
    nl = "\n"
    tab = "\t"
    while not progress.done:
        print(
            Style.RESET_ALL
            + Style.BRIGHT
            + Fore.GREEN
            + f"Performing Document Copy, step {progress.main_progress} of {progress.main_complete_total}:{nl}{tab}elapsed time: {str(datetime.now() - start_time)}"
            + Style.RESET_ALL
        )

        with alive_bar(current_subprocess_total) as bar:
            if current_submessage is not None:
                print(color_wheel[color_wheel_idx] + current_submessage)
                color_wheel_idx = (color_wheel_idx + 1) % len(color_wheel)
            for progress in copy_monitor:
                if progress.sub_msg is not None:
                    current_submessage = progress.sub_msg
                    current_subprocess_total = progress.sub_complete_total
                    break
                bar()
    print(
        Style.RESET_ALL
        + Style.BRIGHT
        + Fore.GREEN
        + f"Finished copying {len(documents)} documents.{nl}Total time: {str(datetime.now() - start_time)}"
        + Style.RESET_ALL
    )


def copy_documents_generator(
    source_server: EscriptoriumConnector,
    destination_server: EscriptoriumConnector,
    documents: List[int],
    project_slug: str,
    ignore_images: bool = False,
    duplicate: bool = False,
) -> Generator[CopyProgress, None, None]:
    """A generator based eScriptorium document copy process.
    It performs the copy and yields back status reports
    about the progress of the copy process. The logfile
    is also used and provides some process messages. Note:
    this function must be called within a for/while loop,
    otherwise it will simply pause at the first yield
    statement and never complete. The caller may manage
    reporting progress to the user as desired.

    Args:
        source_server (EscriptoriumConnector): A connection to the eScriptorium
        server that holds the source for the documents are being copied.
        destination_server (EscriptoriumConnector): A connection to the
        eScriptorium server to which the documents are being copied.
        documents (List[int]): A list of the document PKs on the source_server
        that should be copied to the destination_server.
        project_slug (str, optional): Slug for the project on the destination_server 
        ignore_images (bool, optional): Whether or not to copy images from the
        source_server to the destination_server. Defaults to False.
        duplicate (bool, optional): Whether or not the documents are being
        duplicated on the same eScriptorium server. Defaults to False.
    """
    if project_slug is None or project_slug == "":
        raise Exception("Must provide a project_slug")
    
    total_steps = 9
    current_step = 0
    current_step = current_step + 1
    yield CopyProgress(
        current_step,
        total_steps,
        0,
        2,
        f"Analyzing data for {len(documents)} documents",
    )
    source_docs = (source_server.get_documents()).results

    # If any documents were specified, select only those for copying
    if len(documents) > 0:
        source_docs = [x for x in source_docs if x.pk in documents]

    yield CopyProgress(current_step, total_steps, 1, 2, None)
    dest_projects = destination_server.get_projects().results
    matching_projects = [x for x in dest_projects if x.slug == project_slug]
    if len(matching_projects) == 0:
        raise Exception(f"""Could not find the project {project_slug} on the destination server""")
        #new_project = PostProject(
        #    name=project_name or project_slug
        #)
        #new_project = destination_server.create_project(new_project)
        #destination_server.set_connector_project_by_pk(new_project.id)
    
    if len(matching_projects) > 0:
        destination_server.set_connector_project_by_pk(matching_projects[0].id)
        
    yield CopyProgress(current_step, total_steps, 2, 2, None)
    dest_docs = (destination_server.get_documents()).results

    # Copy the document from source to destination if it doesn't already exist
    current_step = current_step + 1
    yield CopyProgress(
        current_step,
        total_steps,
        0,
        len(source_docs),
        "Creating documents on destination",
    )
    for idx, source_doc in enumerate(source_docs):
        doc_name = source_doc.name + "_duplicate" if duplicate else source_doc.name

        if source_doc.name in [
            x.name for x in dest_docs if (x.project == project_slug) or x.project == ""
        ]:
            logging.info(f"{source_doc.name} is already present on destination")
            yield CopyProgress(current_step, total_steps, idx, len(source_docs), None)
            continue

        logging.debug(
            f"""Copying document {source_doc.pk} {source_doc.name} to destination."""
        )
        new_doc_data = PostDocument(
            name=doc_name,
            project=project_slug,
            main_script=source_doc.main_script,
            read_direction=source_doc.read_direction,
            line_offset=source_doc.line_offset,
            tags=[],  # TODO: Copy tags
        )
        destination_server.create_document(new_doc_data)
        yield CopyProgress(current_step, total_steps, idx, len(source_docs), None)

    current_step = current_step + 1
    yield CopyProgress(
        current_step, total_steps, 0, 0, "Gathering new documents from destination"
    )
    dest_docs = (destination_server.get_documents()).results

    current_step = current_step + 1
    yield CopyProgress(
        current_step, total_steps, 0, len(source_docs), "Gathering images from source"
    )
    dest_docs = (destination_server.get_documents()).results
    src_images: List[List[GetPart]] = []
    for idx, src_doc in enumerate(source_docs):
        if ignore_images:
            yield CopyProgress(current_step, total_steps, idx, len(source_docs), None)
            continue

        # Collect the data for the source images
        src_image_list = (source_server.get_document_parts(src_doc.pk)).results
        src_images.append(src_image_list)
        yield CopyProgress(current_step, total_steps, idx, len(source_docs), None)

    all_images_len = sum([len(x) for x in src_images])
    current_step = current_step + 1
    yield CopyProgress(
        current_step, total_steps, 0, all_images_len, "Copying images to destination"
    )
    count = 0
    for src_doc, images in zip(source_docs, src_images):
        if ignore_images:
            for i in range(all_images_len):
                yield CopyProgress(current_step, total_steps, i, all_images_len, None)
            continue

        dest_doc = [
            x for x in dest_docs if x.name == src_doc.name and x.project == project_slug
        ]
        if len(dest_doc) == 0:
            logging.error(f"Document {src_doc.name} does not exist on destination")
            continue

        dest_doc = dest_doc[0]

        # Collect the data for the destination images
        dest_images = (destination_server.get_document_parts(dest_doc.pk)).results
        for src_image in images:
            logging.debug(
                f"""Copying document {src_doc.pk} image {src_image.filename}."""
            )
            # Check if image already exists
            if src_image.filename in [x.filename for x in dest_images]:
                logging.info(f"{src_image.filename} is already present on destination")
                yield CopyProgress(
                    current_step, total_steps, count, all_images_len, None
                )
                count = count + 1
                continue

            # Get the image
            img_data = source_server.get_image(src_image.image.uri)
            # Move it to the destination
            new_part = PostPart(
                name=src_image.name,
                typology=src_image.typology,
                source=src_image.source,
            )
            destination_server.create_document_part(
                dest_doc.pk, new_part, src_image.filename, img_data
            )
            yield CopyProgress(current_step, total_steps, count, all_images_len, None)
            count = count + 1

    # It doesn't seem that we can have region and line types created automatically
    # when importing an ALTO file, so we need some sort of hack to enable those
    # types for any document, the only way to accomplish this is to create the type
    # on the eScriptorium server instance and then to create a region/line in the
    # document with this type (these can be deleted afterwards).
    current_step = current_step + 1
    yield CopyProgress(
        current_step,
        total_steps,
        0,
        len(source_docs),
        "Gathering source documents region and line types",
    )
    src_region_types: List[List[GetRegionType]] = []
    src_line_types: List[List[GetLineType]] = []
    count = 0
    for idx, src_doc in enumerate(source_docs):
        region_types = source_server.get_document_region_types(src_doc.pk)
        line_types = source_server.get_document_line_types(src_doc.pk)
        src_region_types.append(region_types)
        src_line_types.append(line_types)
        yield CopyProgress(current_step, total_steps, count, len(source_docs), None)
        count = count + 1

    current_step = current_step + 1
    yield CopyProgress(
        current_step,
        total_steps,
        0,
        len(source_docs),
        "Creating region/line types on destination documents",
    )
    for idx, (src_doc, region_types, line_types) in enumerate(
        zip(source_docs, src_region_types, src_line_types)
    ):
        dest_doc = [
            x for x in dest_docs if x.name == src_doc.name and x.project == project_slug
        ]
        if len(dest_doc) == 0:
            logging.error(f"Document {src_doc.name} does not exist on destination")
            continue

        dest_doc = dest_doc[0]

        destination_server.create_document_region_types(
            dest_doc.pk, [x.name for x in region_types]
        )
        destination_server.create_document_line_types(
            dest_doc.pk, [x.name for x in line_types]
        )

        yield CopyProgress(
            current_step,
            total_steps,
            idx,
            len(source_docs),
            None,
        )

    current_step = current_step + 1
    yield CopyProgress(
        current_step,
        total_steps,
        0,
        len(source_docs),
        "Gathering source documents transcriptions",
    )
    transcriptions: List[Tuple[List[GetAbbreviatedTranscription], List[GetPart]]] = []
    for idx, src_doc in enumerate(source_docs):
        # Collect the data for source transcriptions
        src_transcriptions = source_server.get_document_transcriptions(src_doc.pk)
        src_parts = (source_server.get_document_parts(src_doc.pk)).results
        transcriptions.append((src_transcriptions, src_parts))
        yield CopyProgress(current_step, total_steps, idx, len(source_docs), None)

    all_transcriptions_len = sum([len(x[0]) for x in transcriptions])
    current_step = current_step + 1
    yield CopyProgress(
        current_step,
        total_steps,
        0,
        all_transcriptions_len,
        "Copying source documents transcriptions",
    )
    count = 0
    for src_doc, (src_transcriptions, src_parts) in zip(source_docs, transcriptions):
        dest_doc = [
            x for x in dest_docs if x.name == src_doc.name and x.project == project_slug
        ]
        if len(dest_doc) == 0:
            logging.error(f"Document {src_doc.name} does not exist on destination")
            continue

        dest_doc = dest_doc[0]

        # Collect the data for source transcriptions
        for src_transcription in src_transcriptions:
            logging.debug(
                f"""Copying document {src_doc.pk} transcription {src_transcription.name}."""
            )

            downloaded_altos = source_server.download_part_alto_transcription(
                src_doc.pk, [x.pk for x in src_parts], src_transcription.pk
            )
            if downloaded_altos is None:
                logging.error(
                    f"""Could not download ALTO files for document {src_doc.pk} part(s) {", ".join([str(x.pk) for x in src_parts])}."""
                )
                continue
            destination_server.upload_part_transcription(
                dest_doc.pk,
                src_transcription.name,
                f"""export_doc{src_doc.pk}_{src_doc.name}_alto_{datetime.now().strftime("%Y%m%d%H%M")}.zip""",
                BytesIO(downloaded_altos),
                override="off",
            )
            yield CopyProgress(
                current_step, total_steps, count, all_transcriptions_len, None
            )
            count = count + 1

    yield CopyProgress(
        current_step, total_steps, 0, 0, f"Finished copying {len(documents)} documents"
    )

    yield CopyProgress(
        current_step, total_steps, 0, 0, "Finished copying documents", done=True
    )
