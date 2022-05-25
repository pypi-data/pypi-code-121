from typing import List,Tuple
from nlp_tools.metrics.sequence_labeling import end_of_chunk,start_of_chunk

def get_entities(seq: List[str], *, suffix: bool = False) -> List[Tuple[str, int, int]]:
    """Gets entities from sequence.
        Args:
            seq: sequence of labels.
            suffix:
        Returns:
            list: list of (chunk_type, chunk_start, chunk_end).
        Example:
            >>> from nlp_tools.utils.ner_utils import get_entities
            >>> seq = ['B-PER', 'I-PER', 'O', 'B-LOC']
            >>> get_entities(seq)
            [('PER', 0, 1), ('LOC', 3, 3)]
        """
    prev_tag = 'O'
    prev_type = ''
    begin_offset = 0
    chunks = []
    for i, chunk in enumerate(seq + ['O']):
        if suffix:
            tag = chunk[-1]
            type_ = chunk.split('-')[0]
        else:
            tag = chunk[0]
            type_ = chunk.split('-')[-1]

        if end_of_chunk(prev_tag, tag, prev_type, type_):
            chunks.append((prev_type, begin_offset, i -1))
        if start_of_chunk(prev_tag, tag, prev_type, type_):
            begin_offset = i
        prev_tag = tag
        prev_type = type_
    return chunks

def format_ner_result(pred_labels,tokened_sentences,orgin_sentences):
    new_res = [get_entities(seq) for seq in pred_labels]
    final_res = []
    for index, seq in enumerate(new_res):
        seq_data = []
        for entity in seq:
            res_entities: List[str] = []
            for i, e in enumerate(tokened_sentences[index][entity[1]:entity[2] + 1]):
                # Handle bert tokenizer
                if e.startswith('##') and len(res_entities) > 0:
                    res_entities[-1] += e.replace('##', '')
                else:
                    res_entities.append(e)


            value = "".join(res_entities)

            seq_data.append({
                "entity": entity[0],
                "start": entity[1],
                "end": entity[2],
                "value": value,
            })

        final_res.append({
            'sentence': orgin_sentences[index],
            'labels': seq_data
        })
    return final_res

def output_ner_results(origin_texts,predict_labels):
    '''

    '''
    result =[]
    for origin_text,predict_label in zip(origin_texts,predict_labels):
        entity_dict = {}
        entity_dict['sentence'] = origin_text
        labels = []
        for (start_id,end_id,label) in predict_label:

            labels.append({
                "entity": label,
                "start": start_id,
                "end": end_id,
                "value": origin_text[start_id:end_id+1],
            })
        entity_dict['labels'] = labels
        result.append(entity_dict)

    return result


def span_extract_item(start_logits, end_pred):
    '''return type list
    [(labeltype，start,end)]
    '''
    S = []
    for i, s_l in enumerate(start_logits):
        if s_l == 0:
            continue
        for j, e_l in enumerate(end_pred[i:]):
            if s_l == e_l:
                S.append((s_l, i, i + j))
                break
    return S



