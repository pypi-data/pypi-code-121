import spacy
import typer
import logging
from spacy.matcher import Matcher


nlp_instance = None

def get_nlp(use_statistical_sentencizer=False):
    global nlp_instance
    if not nlp_instance:
        logging.info('loading nlp')
        try:
            nlp_instance = spacy.load('en_core_web_lg')
        except:
            raise ValueError('Model not found. Please run `python -m spacy download en_core_web_lg` the first time')
        if not use_statistical_sentencizer:
            # use rule-based sentencizer
            sentencizer = nlp_instance.add_pipe("sentencizer", first=True)
        logging.debug(nlp_instance.pipe_names)
    return nlp_instance

def check_sentences_length(doc, max_length=30):
    logging.info(f'checking sentence length (max_length={max_length})')
    sentences = list(doc.sents)
    reports = []
    for i, sent in enumerate(sentences):
        logging.debug(f'sentence {i}: {sent.text}')
        # sent_length = len(sent)
        words_that_count = [t for t in sent if not t.is_punct]
        words_count = len(words_that_count)
        if words_count > max_length:
            token_index_of_word_outside = words_that_count[max_length].i
            logging.info(f'Sentence {i} is too long: {sent.text}')
            reports.append({
                'warning_type': 'sentence_too_long',
                'expectation': max_length,
                'value': words_count,
                'sentence_index': i,
                'sentence': sent,
                'doc_span_warning': (token_index_of_word_outside, sent.end),
                'explanation': f'length {words_count} greater than {max_length}.'
            })
    n_sents = len(sentences)
    
    return {
        'stats': {
            'criterion_name': 'Sentence length',
            'n_sents_total': n_sents,
            'n_sents_warning': len(reports),
        },
        'reports': reports,
    }

def check_passive_voice(doc, nlp):
    logging.info(f'checking sentence passive voice')
    matcher = Matcher(nlp.vocab)
    # first get start and end of the sentences (used later)
    sentences_start_end = []
    sents = list(doc.sents)
    for sent in sents:
        sentences_start_end.append((sent.start, sent.end))

    passive_rule = [{'DEP':'nsubjpass'},{'DEP':'aux','OP':'*'},{'DEP':'auxpass'},{'TAG':'VBN'}]
    matcher.add('Passive', [passive_rule])
    matches = matcher(doc)
    reports = []
    for m in matches:
        match_id, start, end = m
        sentence_index = next(i for i, (start_sent, end_sent) in enumerate(sentences_start_end) if start_sent <= start and end_sent >= end)
        sent = sents[sentence_index]
        logging.info(f'Sentence {sentence_index} is in passive voice: {sent.text}')
        reports.append({
                'warning_type': 'sentence_too_long',
                'expectation': 'active voice',
                'value': 'passive voice',
                'sentence_index': sentence_index,
                'sentence': sent,
                'doc_span_warning': (start, end),
                'explanation': f'passive voice'
            })
    return {
        'stats': {
            'criterion_name': 'Sentence Passive Voice',
            'n_sents_total': len(sentences_start_end),
            'n_sents_warning': len(reports),
        },
        'reports': reports,
    }

def write_report(result):
    result_strings = []
    n_sents_total = result['stats']['n_sents_total']
    n_sents_warning = result['stats']['n_sents_warning']
    if n_sents_warning:
        color = typer.colors.RED
    else:
        color = typer.colors.GREEN
    result_strings.extend([
        typer.style(f"CRITERION: {result['stats']['criterion_name']}", fg=typer.colors.CYAN, bold=True),
        ': ',
        typer.style(f"{n_sents_warning} out of {n_sents_total}", fg=color, bold=True),
        ' sentences with warning\n'
    ])
    for report in result['reports']:
        sentence = report['sentence']
        doc_span_warning = report['doc_span_warning']
        doc = sentence.doc
        result_strings.extend([
            typer.style(f"(sentence #{report['sentence_index']}): ", fg=typer.colors.MAGENTA, bold=True),
            typer.style(report['explanation'], fg=typer.colors.RED, bold=True),
            '\n',
            doc[sentence.start:doc_span_warning[0]].text_with_ws,
            # ' ',
            typer.style(doc[doc_span_warning[0]:doc_span_warning[1]].text_with_ws, fg=typer.colors.RED, bold=False),
            # ' ',
            doc[doc_span_warning[1]:sentence.end].text_with_ws,
            '\n'
        ])

    message = ''.join(result_strings) + '\n\n'
    typer.echo(message)
   

def check_text(text, max_sentence_length=30, use_statistical_sentencizer=False, ignore_sentence_length=False, ignore_passive_voice=False):
    nlp = get_nlp(use_statistical_sentencizer=use_statistical_sentencizer)
    logging.info('parsing text')
    doc = nlp(text)
    if not ignore_sentence_length:
        length_results = check_sentences_length(doc, max_sentence_length)
        write_report(length_results)
    if not ignore_passive_voice:
        passive_results = check_passive_voice(doc, nlp)
        write_report(passive_results)

    logging.info('done')