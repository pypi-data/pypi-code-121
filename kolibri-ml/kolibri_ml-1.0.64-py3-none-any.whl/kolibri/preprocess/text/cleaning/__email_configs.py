from kolibri.data.text.resources import resources
from pathlib import Path

patterns_file=resources.get(str(Path('modules', 'tokenizers', 'default_regexes.json'))).path


filename_job_functions = resources.get(str(Path('corpora','gazetteers', 'default', 'Job_Functions.txt'))).path
filename_disclaimer = resources.get(str(Path('corpora','gazetteers','default','disclaimers.txt'))).path
filename_salutation = resources.get(str(Path('corpora','gazetteers','default','salutations.txt'))).path
filename_salutation_strict = resources.get(str(Path('corpora','gazetteers','default','salutations_strict.txt'))).path
filename_email_closing = resources.get(str(Path('corpora','gazetteers','default','email_closing.txt'))).path
rejected_emails_formulas=open(resources.get(str(Path('corpora','gazetteers','default','rejected_email.txt'))).path, encoding='utf-8').readlines()
ooo_emails_formulas=open(resources.get(str(Path('corpora','gazetteers','default','out_of_office.txt'))).path, encoding='utf-8').readlines()
sent_from_my_device=open(resources.get(str(Path('corpora','gazetteers','default','sent_from_my_device.txt'))).path, encoding='utf-8').readlines()
email_caution_or_fron_content=open(resources.get(str(Path('corpora','gazetteers','default','email_caution_or_front_content.txt'))).path, encoding='utf-8').readlines()

language = 'en'
functions = open(filename_job_functions, encoding='utf-8').readlines()
disclaimers = open(filename_disclaimer, encoding='utf-8').readlines()
disclaimer_openings = [d.strip() for d in disclaimers if d.strip()]+[d.strip() for d in sent_from_my_device if d.strip()]

salutation_opening_statements = [s.strip() for s in open(filename_salutation, encoding='utf-8').readlines() if s.strip() != ""]
salutation_opening_strict = [s.strip() for s in open(filename_salutation_strict, encoding='utf-8').readlines() if s.strip() != ""]
pattern_disclaimer = r"[\s*]*(?P<disclaimer_text>(" + "|".join(disclaimer_openings) + ")(\s*\w*))"



pattern_salutation = r'(?P<salutation>(^[>|\s-]*\b((' + r'|'.join(
    salutation_opening_statements) + r'))\b)[ ]*(,|\.)?)'

pattern_salutation_colated = r'(?P<salutation>([>|\s-]*\b((' + r'|'.join(
    salutation_opening_strict) + r'))\b)[ ]*(,|\.)?)'


email_closings = [c.strip() for c in open(filename_email_closing, encoding='utf-8').readlines() if c.strip() != ""]

signature_pattern = r'(^[|\.\s>]?)(?P<signature>\s*\b(' + r'|'.join(email_closings) + r')(,|.)?\s*)'

signature_pattern_colated_text = r'([|\.\s>]?)\s*(?P<signature>\b(' + r'|'.join(email_closings) + r')(,|.)?\s*)'

signature_pattern = r'(?P<signature>(^[|\.\s>]?)\s*\b(' + r'|'.join(email_closings) + r')(,|.)?\s*)'
signature_pattern_bis = r'(?P<signature>^\s*\b(' + r'|'.join(email_closings) + r')(,|.)?\s*)'


function_re = ''
for funct in functions:
    function_re += funct.strip('\n') + '|'

function_re = function_re[:-1]

function_re = r'(?P<signature>(([A-Z][a-z]+\s?)+)?(\s?[\|,]\s?)?({})(.+)?)'.format(function_re)

catch_all = r"[0-9A-Za-z一-龠ぁ-ゔァ-ヴー ÑÓżÉÇÃÁªçã$łÄÅäýñëàźiîåüöóąèûìíśćłńé«»°êùáÀèôú⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎 \/@\.:,;\&\?\(\)'´s_\"\*[\]\%+<>#\/\+\s\t_=-]+"
catch_all_oneLine = catch_all.replace('\s', '')[:-1]
catch_all_oneLine = catch_all_oneLine[:1] + '\|' + catch_all_oneLine[1:]


regex_headers = [

    r"((From|To|De|Da|V[ao]n|发件人|Från|Expéditeur)\s*:" + catch_all + "?(((Subject|Objet|Oggetto|Asunto|Onderwerp|Betreff|主题|Ämne|Ass?unto|Tema)\s*:\s?)(?P<subject>(" + catch_all_oneLine + ")+))|((Sent\sat|Enviado\sa|Enviada à\(s\)|Datum|Date|Envoyé|Verzonden|Sent)\s*:" + catch_all_oneLine + "))",
    r"On\s+(\d{2}|Mon(day)?|Tue(sday)?|Wed(nesday)?|Thu(rsday)?|Friday|Sat(urday)?|Sun(day)?)" + catch_all + "(wrote):",
    r"\s{0, 10}(\d{1,2})?\s?(Jan|Feb|Mar|Apr|Mai|Jun|Jul|Aug|Sep|Nov|Oct|Dec)\s?(\d{1,2})?,\s+\d{2}:\d{2}\s+UTC$",
    r"(Op|Le|On)\s.*\s(om|à|at|\d{2}:\d{2})\s*.*\s?.*(schreef|a écrit|wrote|geschreven)\s*(:)?"

]


date_regex_from_header="(Sent\sat|Enviado(\s(a|el))?|Enviada à\(s\)|Gesendet|Envoyés|Datum|Date|Data|Fecha|Inviato|Envoyé(\s+le)?|Verzonden|Verstuurd|Sent)\s*:\s*(?P<Sent_Date>(.*$))|(Op|Le|On)\s*(?P<Sent_Date>(.*))(om|à|at|schreef|wrote|a écrit)"