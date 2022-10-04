import os.path, requests, urllib.request, time, re, readline, yaml, html
from bs4 import BeautifulSoup

import seldon.core.path
import seldon.core.logging

class DiseaseCommands:
  def command_disease_cache(self):
    """Cache the rare disease symptom database and create the word-usage frequency table"""
    pass

  def command_drug_cache(self):
    """Cache the drug database"""
    pass


def rlinput(prompt, prefill=''):
  readline.set_startup_hook(lambda: readline.insert_text(prefill))
  try:
    return input(prompt)  # or raw_input in Python 2
  finally:
    readline.set_startup_hook()

class DrugData:
  def __init__(self):
    self.base_url = 'https://www.centerwatch.com'
    self.database_path = os.path.abspath(
      os.path.join(os.path.dirname(os.path.dirname(__file__)), 'drugs', 'db_raw.yaml'))
    self.database_load()

  def database_load(self):
    self.db = {}
    if os.path.exists(self.database_path):
      with open(self.database_path) as f:
        try:
          self.db = yaml.safe_load(f)
        except yaml.YAMLError as exc:
          print(exc)

  def database(self):
    return self.db

  def database_save(self):
    with open(self.database_path, 'w') as f:
      f.write(yaml.dump(self.db))

  def update_drug_list(self):
    match = '/directories/1067-fda-approved-drugs/listing/'
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWX':
      page = 1
      while True:
        page_url = self.base_url + f'/directories/1067-fda-approved-drugs/{letter}?page={page}'
        response = requests.get(page_url)
        # print(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        hits = 0
        for e in soup.findAll('a'):
          if match not in e['href']: continue
          if match == e['href']: continue
          url = self.base_url + e['href']
          name_raw = str(e.contents[0])
          m = re.match(r'^(.+?)( \((.+)\))?$', name_raw)
          name_trade = str(m.group(1))
          name_generic = str(m.group(3))
          if name_raw not in self.db:
            self.db[name_raw] = {
              'names': {
                'raw': name_raw,
                'trade': name_trade,
                'generic': name_generic,
              },
              'url': url
            }
          hits += 1
        if hits == 0: break
        page += 1
        print(letter, page, hits, len(self.db))
        self.database_save()
      time.sleep(1)
    self.database_save()

  def _fix_names(self, which, default):
    default = default.replace('for injection', ' ')
    default = default.replace('HCL', ' ')
    default = default.replace(' gel', ' ')
    default = default.replace('vaginal insert', ' ')
    default = default.replace('injectable suspension', ' ')
    default = default.replace('transdermal system', ' ')
    default = default.replace('inhalation powder', ' ')
    default = default.replace('extended-release', ' ')
    default = default.replace('oral powder', ' ')
    default = default.replace('tablets', ' ')
    default = default.replace('injection', ' ')
    default = default.replace('ophthalmic solution', ' ')
    default = default.replace('hydrochloride', ' ')
    default = default.replace('sodium', ' ')
    default = re.sub(r'\s+', ' ', default.strip())
    default = ', '.join([v.strip() for v in default.split(' and ')])
    default = ', '.join([v.strip() for v in default.split(' + ')])
    default = ', '.join([v.strip() for v in default.split('/')])
    default = ', '.join([v.strip() for v in default.split(';')])
    default = re.sub(r',+', ',', default.strip())
    # ret = input(f"{'generic':<20s} ({default:<60s}): ").strip()
    ret = rlinput(f"{'generic':<20s} ({default:<60s}): ", default if default != 'None' else '').strip()
    if ret == '': ret = default
    return ret

  def fix_names(self):
    for drug in dd.database().values():
      # skip if we've already updated this
      if drug['names'].get('ok', False): continue
      # skip case where there is a single trade name and no generic name
      if len(drug['names']['trade'].split(' ')) == 1 and drug['names']['generic'] == 'None': continue
      # skip the simplest case
      if re.match(r'^(\S+?) \(\S+\)$', drug['names']['raw']): continue

      # do something about these
      pp(drug['names'])
      drug['names']['generic'] = self._fix_names('generic', drug['names']['generic'])
      drug['names']['trade'] = self._fix_names('trade', drug['names']['trade'])
      drug['names']['ok'] = True
      self.database_save()

  def repurpose(self):
    ret = {}
    for k, v in self.db.items():
      for g in [i.strip() for i in v['names']['generic'].split(',')]:
        ret[g] = ret.get(g, set())
        ret[g].add(v['names']['trade'])

    items = sorted(list(ret.items()), key=lambda i: len(i[1]), reverse=True)
    c = 0
    counts = {}
    for k, v in items:
      print(f"{k:<50s}: {len(v):5,}: {', '.join(list(v))}")
      counts[len(v)] = counts.get(len(v), 0) + 1
      if len(v) == 1: c += 1

    print()
    print(f"{c:,} singlets, {len(ret) - c:,} multiplets")
    print(f"{'# of brands':11s}\t{'number of generics':20s}")
    for k, v in sorted(counts.items()):
      print(f"{k:11,}\t{v:20,}")

  def information_page(self, url):
    """Get the html for a page describing the drug"""

    # if there is a local cache of the page, take that instead of hammering the server
    local_path = os.path.join(
      os.path.dirname(self.database_path), 'cached',
      url.replace('https://', '').replace('/', '_').replace(':', '_')
    ).replace(
      'www.centerwatch.com_directories_1067-fda-approved-drugs_listing_', ''
    )
    if os.path.exists(local_path):
      with open(local_path) as f: html = f.read()
      return html

    # don't hammer the server too much
    if self.last_fetched is None: self.last_fetched = 0
    if int(time.time()) - self.last_fetched < 1:
      print("sleeping")
      time.sleep(1)

    html = requests.get(page_url).text
    with open(local_path, 'w') as f:
      f.write(html)
    self.last_fetched = time.time()
    return html

  def information_base(self, html):
    """Get the base information out of the page that is simple to parse"""
    meta = {}

    soup = BeautifulSoup(html, 'html.parser')

    # get the contact information
    contact_name = 'None'
    c = soup.findAll('div', class_='contact directory-listing-profile__company-contact')
    if len(c) > 0: contact_name = c[0].contents[0].split(':', 2)[1].strip()
    meta['contact_name'] = contact_name

    # get the contact information
    contact_name = 'None'
    c = soup.findAll('div', class_='contact directory-listing-profile__company-contact')
    if len(c) > 0: contact_name = c[0].contents[0].split(':', 2)[1].strip()
    meta['contact_name'] = contact_name

    contact_display = 'None'
    contact_url = 'None'
    w = soup.findAll('div', class_='url directory-listing-profile__url-link')
    if len(w) > 0:
      w = w[0].findAll('a')[0]
      contact_display = w.contents[0]
      contact_url = w['href']
    meta['contact_display'] = contact_display
    meta['contact_url'] = contact_url

    # get the approval and company name
    approval_date = []
    company_name = []
    for tag in soup.findAll('div', class_='contact directory-listing-profile__master-detail'):
      name, val = [v.strip() for v in tag.contents[0].split(':')]
      if name == 'Approval Date': approval_date.append(val)
      if name == 'Company Name': company_name.append(val)
    meta['approval_date'] = ', '.join(approval_date)
    meta['company_name'] = ', '.join(company_name)

    return meta

  def to_text(self, contents):
    ret = str(html.unescape(contents))
    ret = ret.replace('\n', ' ')
    ret = ret.replace("<br>", '\n')
    ret = re.sub(r'<li>(.+?)</li>', r"__nl____indent__- \1__nl__", ret)
    ret = ret.replace('\xa0', ' ')
    ret = re.sub(r'\s+', ' ', ret)
    ret = re.sub('<.+?>', '', str(ret))
    ret = ret.strip()
    return ret

  def information_header(self, contents):
    key = self.to_text(contents)
    if key == '': return [None, None]

    renames = {
      'General Information': 'general',

      'Indications': 'indications',

      'Mechanism of Action': 'mechanism',
      'Mechanism Of Action': 'mechanism',
      'Mechanism of Actio': 'mechanism',
      'Mechansim of Action': 'mechanism',

      'Side Effects': 'side effects',
      'Side effects': 'side effects',

      'Trial Results': 'trial',
      'Clinical Results': 'trial',
      'Clinical Trials': 'trial',
      'Clinical Trial Results': 'trial',
      'Clinical TrialResults': 'trial',

      'FDA Approval': 'approval',

      'Dosing/Administration': 'dosing',
      'Dosage/Administration': 'dosing',

      'Literature References': 'literature',

      'Additional Information': 'additional',
    }
    if key in renames: return [renames[key], None]

    # Trade Name (generic name)
    if re.match(r'.+?\s*?\(.+?\)$', key, re.IGNORECASE):
      return ['generals', None]

    # Trade Name (generic name) - 4 indications
    if re.match(r'.+?\s*?\(.+?\)\s*?[:–-]?\s*?\d+\s*?indications?', key, re.IGNORECASE):
      return ['indications', None]

    # Indication 3 - disease name
    m = re.match(r'Indications?\s*?(\d+)\s*?[:–-]?\s*?(.+)', key, re.IGNORECASE)
    if m: return [f'indication_details', f'__indent__- {m.group(1)}:2d) {m.group(2)}']

    # Activella is specifically indicated for moderate...
    m = re.match(r'.+? is specifically indicated for (.+)', key, re.IGNORECASE)
    if m: return ['indication', f'__indent__-  1) {m.group(1)}']

    # Monotherapy and adjunctive therapy of complex partial seizures and simple and complex absence seizures; adjunctive therapy in patients with multiple seizure types that include absence seizures
    m = re.match(
      r'Monotherapy .+? of (complex .+? seizures); adjunctive therapy in patients with (multiple .+? seizures)', key,
      re.IGNORECASE)
    if m: return [
      'indication',
      f'__indent__-  1) {m.group(1)}',
      f'__indent__-  2) {m.group(2)}'
    ]

    # Diovan - Indication 1 - hypertension
    m = re.match(r'.+? - Indications? (\d+) - (.+)', key, re.IGNORECASE)
    if m: return ['indication', f'__indent__-  {m.group(1)}) {m.group(2)}']

    # Diovan HCT - for the treatment of hypertension, to lower blood pressure, in patients not adequately controlled with monotherapy or as initial therapy
    m = re.match(r'.+? - for the treatment of (.+)', key, re.IGNORECASE)
    if m: return ['indication', f'__indent__-  1) {m.group(1)}']

    # Clinical Trial Results for indications 1-3:'
    m = re.match(r'Clinical Trial Results for indications', key, re.IGNORECASE)
    if m: return ['trial', None]

    ##############################################
    # some edge cases
    ##############################################

    # Depakote (divalproex sodium) delayed-release tablets - 4 indications
    if re.match(r'.+?\s*?\(.+?\)\s*?.+?[:–-]?\s*?\d+\s*?indications?', key, re.IGNORECASE):
      return ['indications', None]

    # Depakote (divalproex sodium) delayed-release tablets
    if re.match(r'Depakote \(divalproex sodium\) delayed-release tablets', key, re.IGNORECASE):
      return [None, None]

    # Depakote Sprinkle Capsules (divalproex sodium delayed release capsules)
    if re.match(r'Depakote Sprinkle Capsules \(divalproex sodium delayed release capsules\)', key, re.IGNORECASE):
      return [None, None]

    # Depakote ER (divalproex sodium) extended-release tablets
    if re.match(r'Depakote ER \(divalproex sodium\) extended-release tablets', key, re.IGNORECASE):
      return [None, None]

    # Depakote ER (divalproex sodium) extended-release tablets
    if re.match(r'Paxil( CR)?$', key, re.IGNORECASE):
      return ['general', None]

    # Prempro/Premphase - 3 indications
    if re.match(r'Prempro/Premphase - 3 indications$', key, re.IGNORECASE):
      return ['indications', None]

    # The recommended dose of the product is 44 mcg three
    if re.match(r'^The recommended dose of the product is 44 mcg three', key, re.IGNORECASE):
      return ['_same_', key]

    # Reminyl is given in a tablet formulation
    if re.match(r'^Reminyl is given in a tablet formulation', key, re.IGNORECASE):
      return ['_same_', key]

    # VESIcare LS is supplied as a liquid oral suspension
    if re.match(r'^VESIcare LS is supplied as a liquid oral suspension', key, re.IGNORECASE):
      return ['_same_', key]

    sys.exit(f'lots to do for "{key=}"')

  def information_sections(self, html):
    desc = {}
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.findAll('div', class_='directory-listing-profile__description')[0]
    current_key = 'general'
    for tag in soup.findAll(recursive=False):
      contents = tag.contents
      if len(contents) == 0: continue

      # headers are the sections of the information text
      if re.match(r'^h2$', tag.__name__):
        key, *to_add = self.information_header(contents[0])
        if key is None: continue
        if key == '_same_': key = current_key
        current_key = key
        desc[current_key] = desc.get(key, [])
        if to_add[0] is not None:
          for a in to_add:
            desc[current_key].append(a)
      else:
        d = desc[current_key] = desc.get(current_key, [])
        c = ' '.join([str(c) for c in contents])
        c = re.sub(r'\s+', ' ', c)
        c = self.to_text(c)
        c = c.replace('__nl__', "\n")
        for line in c.split("\n"):
          line = line.strip()
          if 'Scroll down for' in line: continue
          line = line.replace('__indent__', '  ')
          if len(line) > 0:
            d.append(line)
    # should save it all
    return desc

  def information_section_format(self, text):
    r = "\n\n".join(text)
    r = r.replace('__indent__', '  ')
    r = r.replace("\n\n  - ", "\n  - ")
    return r

  def information_extract_indications(self, sections):
    if 'indications' in sections: return

    # special case where there is a section in general like
    # is indicated for: and the next lines are items starting with a dash
    ind_words = ['specifically indicated', 'are indicated for', 'is indicated for']
    text = self.information_section_format(sections.get('general', []))
    for par in text.split('\n\n'):
      if "\n  - " not in par: continue
      hdr, *body = par.split('\n')
      ok = any([w in hdr for w in ind_words])
      if not ok: continue
      i = 0
      for row in body:
        row = re.sub(r'^\s*?-\s*?', '-', row)
        if not row.startswith('-'): continue
        row = row[1:].strip()
        i += 1
        ind = sections['indications'] = sections.get('indications', [])
        ind.append(f'__indent__- {row}')
      # pp(sections['indications'])
      if i > 0: return

    regexes = [
      # some specific ones first
      r'Adcetris is specifically approved for 1\) (.+?) and 2\) (.+)',
      r'Aggrenox works to prevent the (clotting in patients)',
      r'Activella is a combination (.+)',
      r'Adderall has been indicated for use in children three years of age and older with (ADHD)',
      r'has been approved for treatment of (ADHD) in children',
      r'is specifically indicated for persistent/recurrent (Chronic Thromboembolic.+?) after surgical treatment',
      r'is specifically indicated for use in adults and children with (hemophilia A \(congenital Factor VIII deficiency\))',
      r'specifically indicated for the preventive treatment of (migraine)',
      r'specifically indicated for the topical treatment of (acne vulgaris)',
      r'specifically indicated as a (local anesthetic indicated for ocular surface anesthesia during ophthalmologic procedures)',
      r'specifically indicated for the prevention of (acute and delayed nausea and vomiting associated with initial and repeat courses of cancer chemotherapy)',
      r'indicated for treatment of (external genital and perianal warts in adults)',
      r'has been approved for the prevention and control of (bleeding in subjects with Factor IX deficiency due to hemophilia B.)',
      r'specifically indicated in adults and children with (hemophilia B for control and prevention of bleeding episodes)',
      r'specifically indicated for use in adults and pediatric patients aged 9 months and older for the topical treatment of (impetigo)',
      r'have been approved by the FDA as a once-daily adjunct to diet for the reduction of .+? (hyper-cholesterolemia)',
      r'specifically indicated for the maintenance treatment of (asthma) as prophylactic therapy in adult and adolescent patients 12 years of age and older',
      r'specifically indicated as a first-line therapy to lower blood glucose in people with (type II diabetes)',
      r'specifically indicated in combination .+? of (actinic keratoses \(AKs\))',
      r'Amevive reduces (immune cell counts) which could increase the chance of developing infection or malignancy',
      r'specifically inidicated as a treatment to improve walking in patients with (multiple sclerosis)',
      r'extended release skeletal muscle relaxant which relieves (muscle spasm)',
      r'indicated for patients treated with rivaroxaban and apixaban, when reversal of (anticoagulation)',
      r'indicated for men with (primary hypogonadism or hypogonadotropic hypogonadism)',
      r'approved by the FDA as a treatment for (hypogonadism)',
      r'specifically indicated for use by females of reproductive potential to prevent (pregnancy)',
      r'specifically indicated for the long-term, once-daily, maintenance treatment of airflow obstruction in patients with (chronic obstructive pulmonary disease, including chronic bronchitis and/or emphysema)',
      r'indicated as an antidote for (ethylene glycol poisoning)',
      r"specifically indicated for the acute, intermittent treatment of (hypomobility,.+? Parkinson’s disease)",
      r'Aptiom is specifically indicated as adjunctive treatment for (partial-onset seizures)',
      r'is indicated for the adjunctive treatment of (adult periodontitis following scaling and root planing)',
      r'has been approved as a treatment for (advanced breast cancer in postmenopausal women whose disease has progressed following therapy with tamoxifen)',
      r'has been approved as a preventative treatment for (deep vein thrombosis \(DVT\))',
      r'specifically indicated for the once-daily maintenance treatment of (asthma)',
      r'to treat post-menopausal (advanced breast cancer in patients for whom treatment with tamofixen was ineffective)',
      r'specifically indicated as a component of a multi-agent chemotherapeutic regimen for (acute lymphoblastic leukemia \(ALL\) in pediatric and young adult patients age 1 month to 21 years)',
      r'prevention of (postoperative nausea and vomiting \(PONV\)), either alone or in combination with an antiemetic of a different class',
      r'the treatment of adult patients with (active, autoantibody-positive, systemic lupus erythematosus)',
      r'(Newly-diagnosed chronic phase Ph+ chronic myelogenous leukemia \(CML\))',
      r'(Chronic, accelerated, or blast phase Ph+ CML with resistance or intolerance to prior therapy)',
      r'specifically indicated to slow the loss of ambulation in symptomatic pediatric patients 3 years of age and older with (late infantile neuronal ceroid lipofuscinosis type 2 \(CLN2\))',
      r'Caverject is the first prescription drug approved for (impotence)',
      r'Cetrotide has been developed to prevent (premature ovulation) in women undergoing controlled ovarian stimulation for assisted reproductive technologies \(ART\)',
      r'(Seasonal Allergic Rhinitis): ',
      r'(Perennial Allergic Rhinitis): ',
      r'(Chronic Idiopathic Urticaria): ',
      r'approved the first one-pill combination of the two most widely used antiretroviral medications for (AIDS and HIV infection)',
      r'Daptacel is a (diptheria and tetanus toxoids and acellular pertussis vaccine adsorbed \(DTaP\))',
      r'Droxia has been approved for people who have had three or more painful episodes with (sickle-cell)',
      r'(acute and delayed nausea and vomiting associated with initial and repeat courses of highly emetogenic cancer chemotherapy (HEC) including high-dose cisplatin)',
      r'(nausea and vomiting associated with initial and repeat courses of moderately emetogenic cancer chemotherapy \(MEC\))',
      r'(In patients 6 years of age and older for single-dose infiltration to produce postsurgical local analgesia)',
      r'(In adults as an interscalene brachial plexus nerve block to produce postsurgical regional analgesia)',
      r'(for active immunization for the prevention of influenza)',
      r'(trivalent recombinant vaccine for seasonal influenza)',
      r' for the maintenance treatment of asthma and the prevention of (bronchospasm in reversible obstructive airways disease). Foradil is also indicated for the acute prevention of (exercise-induced bronchospasm \(EIB\)), when administered on an occasional, as needed basis',
      r'(reduce serum phosphate levels .+)',
      r'approved Frova \(frovatriptan succinate\) for the (.+)',
      r'first (atypical antipsychotic) medication',
      r'(immunization against diphtheria, tetanus, and pertussis)',
      r'is an (anticancer drug that inhibits an enzyme \(tyrosine kinase\) present in lung)',
      r'approved for use as a replacement therapy for any form of (diminished or absent thyroid function)',
      r'reducing the incidence of (ifosfamide-induced hemorrhagic cystitis)',
      r'Treatment of (inflammatory papules and pustules of rosacea)',
      r'(Prevention of pregnancy) may be due to subsequent',
      r'acceptable form of therapy for (various circulatory disorders including angina, pulmonary hypertension, and congestive heart failure)',
      r'provides (month-long contraceptive protection)',
      r'indicated in adults and children 4 years of age and older for the treatment or prevention of (.+)',
      r'relieves (pain in nerve endings and associated symptoms caused by migraine headaches)',
      r'Reminyl is an (Alzheimer\'s treatment)',
      r'recently approved by the FDA for treatment of (open-angle glaucoma or ocular hypertension)',
      r'Selzentry is specifically indicated, in combination with other antiretroviral agents, for treatment experienced (adult patients infected with only CCR5-tropic HIV-1 detectable, who have evidence of viral replication and HIV-1 strains resistant to multiple antiretroviral agents)',
      r'class of treatment that works differently from the other (attention-deficit/hyperactivity disorder)',
      r'(approved for marketing only under a special restricted distribution program approved by the FDA).',
      r'approved as a new (antiepileptic drug proven to reduce the frequency of seizures).+? indicated as adjunctive therapy for (partial onset seizures), the most common seizure type, in adults',
      r'for (treatment of adults with newly-diagnosed low-risk acute promyelocytic leukemia \(APL\))',
      r'approved by the FDA for the (short-term \(five days or less\) management of acute pain)',
      r'approved for use in (replenishing iron in patients receiving erythropoietin \(a hormone that stimulates red blood cell production\) and undergoing chronic hemodialysis)',
      r'speicifcally approved in combination with a proton pump inhibitor for adults with (.+)',
      r'approved for (obesity management)',
      r'approved for the reduction of (mortality in adults with severe sepsis)',
      r'is expressed by more than 90% of (colorectal cancers), as well as by a large number of (other carcinomas, including esophageal, stomach, lung, breast, pancreas, uterus, and ovarian cancer)',

      r'specifically approved (.+)',
      r'over-the-counter formula for (.+)',
      r'specifically indicated as adjunctive therapy to improve (.+)',
      r'the treatment of documented, life-threatening (.+)',
      r'specifically indicated as adjunctive therapy in the treatment of (.+)',
      r'the maintenance of normal sinus rhythm (.+)',
      r'specifically indicated to help protect individuals six months of age and older against (.+)',
      r'is indicated in the treatment of (.+)',
      r'specifically indicated for (.+)',
      r'for the relief of the symptoms of (.+)',
      r'indicated for the pevention of (.+)',
      r'specifically indicated for the maintenance treatment of ',
      r'specifically indicated for use in the treatment of (.+)',
      r'has been approved as a treatment for (.+)',
      r'approved for the symptomatic treatment of (.+)',
      r'specifically indicated for the treatment of (.+)',
      r'for the treatment of (.+)',
      r'indicated for the first-line treatment of (.+)',
      r'indicated for the management of (.+)',
      r'approved for the treatment (.+)',
      r'indicated for the prophylaxis and chronic treatment of (.+)',
      r'approved as a new therapy for treating (.+)',
      r'indicated as an adjunct to diet and exercise to improve (.+)',
      r'indicated for the prophylaxis and the relief of (.+)',
      r'specifically indicated to reduce the frequency of (.+)',
      r'specifically approved for (.+)',
      r'the treatment of (.+)',
      r'as an adjunct therapy to diet for prevention of (.+)',
      r'specifically indicated to improve (.+)',
      r'specifically indicated to treat (.+)',
      'treatment in the management of (.+)',
      'indicated as an (.+)',
      'specifically indicated to reduce the risk of (.+)',
      'specifically indicated to decrease the incidence of (.+)',
      'specifically indicated to (.+)',
      'specifically indicated as a treatment to reduce the risk of (.+)',
      r'indicated for the prevention of (.+)',
      r'specifically indicted for the reduction of (.+)',
      r'specifically indicated as a component of adjuvant therapy in patients with evidence of (.+)',
      r'specifically indcated for (.+)',
      r'specifically indicated (.+)',
      r'is indicated for (.+)',
      r'are indicated for use in the (.+)',
      r'indicated for (.+)',

    ]
    i = sections['indications'] = []
    hits = 0
    for line in sections.get('general', []):
      had_hit = False
      for r in regexes:
        for m in re.findall(r, line):
          if isinstance(m, str): m = [m]
          for m_ in m:
            m_ = m_.split("\n")[0].split(". ")[0]
            o = (f'- {m_}').rstrip()
            i.append('__indent__' + o)
            # if not had_hit: print(f'{r=}')
            hits += 1
            had_hit = True
        # only one regex can be applied in a single line
        if had_hit: break

    if hits > 0: return

    print(self.information_section_format(sections.get('general', [])))
    print("\n".join(i).replace('__indent__', '  '))
    sys.exit('!!!!!!!!!!!!')

  def information_hard_coded_indications(self, sections, code):
    if code == '3337-colazal-balsalazide-disodium':
      sections['indications'] = ['__indent__  1) mild to moderate ulcerative colitis']
      return
    if code == '3330-climara-pro-estradiol-levonorgestrel-transdermal-system':
      sections['indications'] = [
        '__indent__  - vasomotor symptoms of menopause, approved June 1999',
        '__indent__  - postmenopausal osteoporosis, approved 2005',
      ]
    if code == '3430-edluar-zolpidem-tartrate':
      sections['indications'] = [
        '__indent__  - short-term treatment of insomnia characterized by difficulties with sleep initiation.',
      ]
      return
    if code == '3512-fabrazyme-agalsidase-beta':
      sections['indications'] = [
        '__indent__  - provide an exogenous source of a-galactosidase A in Fabry disease patients',
      ]
      return
    if code == '3605-herceptin-hylecta-trastuzumab-and-hyaluronidase-oysk':
      sections['indications'] = [
        '__indent__  - Adjuvant treatment of adults with HER2 overexpressing node positive or node negative',
        '__indent__  - Metastatic Breast Cancer in adults',
      ]
      return
    if code == '3901-norditropin-somatropin-injection':
      sections['indications'] = [
        '__indent__  - Treatment of pediatric patients with growth failure due to inadequate secretion of endogenous growth hormone (GH), short stature associated with Noonan syndrome, short stature associated with Turner syndrome, short stature born small for gestational age (SGA) with no catch-up growth by age 2 to 4 years, Idiopathic Short Stature (ISS), and growth failure due to Prader-Willi Syndrome',
        '__indent__  - Replacement of endogenous GH in adults with growth hormone deficiency',
      ]
      return
    if code == '3926-nuzyra-omadacycline':
      sections['indications'] = [
        '__indent__  - Adult patients with community-acquired bacterial pneumonia (CABP) caused by the following susceptible microorganisms: Streptococcus pneumoniae, Staphylococcus aureus (methicillin-susceptible isolates), Haemophilus influenzae, Haemophilus parainfluenzae, Klebsiella pneumoniae, Legionella pneumophila, Mycoplasma pneumoniae, and Chlamydophila pneumoniae',
        '__indent__  - Adult patients with acute bacterial skin and skin structure infections (ABSSSI) caused by the following susceptible microorganisms: Staphylococcus aureus (methicillin-susceptible and -resistant isolates), Staphylococcus lugdunensis, Streptococcus pyogenes, Streptococcus anginosus grp. (includes S. anginosus, S. intermedius, and S. constellatus), Enterococcus faecalis, Enterobacter cloacae, and Klebsiella pneumoniae',
      ]
      return
    if code == '4313-trelstar-triptorelin-pamoate':
      sections['indications'] = [
        '__indent__  - palliative treatment of advanced prostate cancer',
      ]
      return

  def information(self):
    """Get the drug information"""
    max_i = len(self.db)
    t0 = time.time()
    keys = list(self.db.keys())
    for i, k in enumerate(keys):
      v = self.db[k]
      if 'meta' not in v:
        # get the page from the web or from a local cache
        code = os.path.basename(v['url'])
        html = self.information_page(v['url'])
        # get the simplest-to-fetch data from that page
        v['meta'] = self.information_base(html)

        sections = v['meta']['sections'] = self.information_sections(html)
        self.information_section_format(sections)
        self.information_hard_coded_indications(sections, code)
        self.information_extract_indications(sections)
      eta = int((time.time() - t0) / (i + 1) * (max_i - i - 1))
      units = 'seconds'
      if eta > 90:
        eta = eta / 60
        units = 'minutes'

      sys.stderr.write(f'step {i + 1:5,} of {max_i:5,} [{100.0 * (i + 1) / max_i:.1f}%] done in {eta:5.1f} {units}\n')

    keys = sorted(keys, key=lambda e: len(self.db[e]['meta']['sections']['indications']), reverse=True)
    for key in keys:
      m = re.search(r'^(.+?)\s*?\((.+?)\)', key)
      if m:
        trade_name = m.group(1)
        generic_name = m.group(2)
        if generic_name.endswith('mab'): continue

      s = self.db[key]['meta']
      if len(s['sections']['indications']) == 1: continue

      print(key)
      print(s['company_name'])
      print(self.db[key]['url'])
      if s['contact_url'] != 'None':
        print(s['contact_url'])
        pass
      print('approved:', s['approval_date'])
      ar = self.annotate_rare(self.information_section_format(s['sections']['indications']))
      print(ar)
      print()
      print('-' * 200)

  def annotate_rare(self, text):
    rd = self.rare_diseases()
    ret = []
    for k in rd:
      if len(k) <= 3: continue
      new_k = k.lower().replace('(', r'\(').replace(')', r'\)').replace('[', '\]').replace(']', '\]')
      # print(k)
      try:
        if not re.search(r'\b' + new_k + r'\b', text.lower(), re.IGNORECASE): continue
      except Exception:
        print("failure to match")
        print(new_k)
      ret.append(k + ' => ' + ' -OR- '.join([a[0] for a in rd[k]]))
    # sys.exit()
    oret = "\npossible rare diseases\n - " + "\n - ".join(ret)
    if len(ret) > 0:
      text += oret
      # print("~" * 100)
      # print(oret)
      # print("~" * 100)
    return text

  def rare_disease_fix_pren_commas(self, text):
    text = re.sub(r'\band\b', '&', text)
    depth = 0
    ret = []
    for c in list(text):
      if c == '(': depth += 1
      if c == ')': depth -= 1
      if depth > 0 and c == ',': c = '|'
      if depth > 0 and c == '&': c = '+'
      ret.append(c)
    ret = ''.join(ret)
    ret = re.sub(r'\s+', ' ', ret.replace('&', ' and '))
    ret = ret.replace('| included', ' included')
    return ret

  def rare_diseases(self, reset=False):
    # a = 'Chromosome 4, Partial Trisomy 4q (4q21-qter to 4q32-qter, included), Chromosome 4, Partial Trisomy 4q (4q2 and 4q3, included), Distal 4q Trisomy, Dup(4q) Syndrome, Partial, Duplication 4q Syndrome, Partial, Partial Trisomy 4q Sayndrome'
    # print(self.rare_disease_fix_pren_commas(a))
    # sys.exit()

    if hasattr(self, '_rare_diseases'): return self._rare_diseases
    local_path = os.path.join(os.path.dirname(self.database_path), 'rare_diseases.yaml')
    if os.path.exists(local_path) and not reset:
      with open(local_path) as f:
        self._rare_diseases = yaml.safe_load(f)
        return self._rare_diseases

    ret = {}
    dirs = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['0-9']
    self.last_fetched = 0
    for dir in dirs:
      print(dir)
      headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
      }
      url = 'https://rarediseases.org/?post_type=rare-diseases&s=' + dir
      html = requests.get(url, headers=headers).text

      soup = BeautifulSoup(html, 'html.parser')
      # print(soup.prettify())
      for tag in soup.findAll('article', 'type-rare-diseases'):
        link = tag.find('a')
        url = link['href']
        name = link.contents[0]
        try:
          rest = tag.find('em').contents[0].replace('Also known as: ', '')
        except AttributeError:
          rest = ''
        if rest.startswith('Subdivisions'): continue

        rest = re.sub(r'[\s\n]+', ' ', rest)
        orest = rest
        rest = self.rare_disease_fix_pren_commas(rest)
        rest = [r.strip() for r in re.split(r',|and', rest)]
        nrest = []
        for r in rest:
          if '(' not in r:
            nrest.append(r)
            continue

          m = re.search(r'^\((.+?)\)(.+?)$', r)
          if m:
            for w in [w_.strip() for w_ in m.group(1).strip().split('|')]:
              nrest.append(w + ' ' + m.group(2).strip())
            continue

          m = re.search(r'^(.+?)\((.+?)\)$', r)
          if m:
            nrest.append(m.group(1).strip())
            nrest.append(m.group(2).strip())
            continue

          # isodicentric chromosome 15 syndrome [Idic(15)]
          m = re.search(r'^(.+?) \[(.+?)\]', r.strip())
          if m:
            nrest.append(m.group(1).strip())
            nrest.append(m.group(2).strip())
            continue

          # Hemoglobin H (HbH) disease
          m = re.search(r'^(.+?) \((.+?)\) (.+)$', r.strip())
          if m:
            nrest.append(m.group(1).strip() + ' ' + m.group(3).strip())
            nrest.append(m.group(2).strip() + ' ' + m.group(3).strip())
            continue

          # Hemoglobin H (HbH) disease
          m = re.search(r'^\((.+?)\)$', r.strip())
          if m:
            nrest.append(m.group(1).strip())
            continue

          # del(10q)
          m = re.search(r'^(del|dup)\(\d+[pq]\) syndrome$', r.strip(), re.IGNORECASE)
          if m:
            nrest.append(r)
            continue

          m = re.search(r'^(.+?)\((s)\) (.+?)$', r.strip(), re.IGNORECASE)
          if m:
            nrest.append(m.group(1) + ' ' + m.group(3))
            nrest.append(m.group(1) + m.group(2) + ' ' + m.group(3))
            continue

          if r == 'striatonigral degeneration (SND':
            nrest.append('striatonigral degeneration')
            nrest.append('SND')
            continue

          if r.startswith('autosomal dominant dopa-responsive dystonia'):
            nrest.append('autosomal dominant dopa-responsive dystonia')
            nrest.append('autosomal dominant segawa syndrome')
            nrest.append('DYT5 dystonia')
            nrest.append('GTP cyclohydrolase 1-deficient dopa-responsive dystonia')
            nrest.append('guanosine triphosphate cyclohydrolase I deficiency')
            nrest.append('progressive dystonia with marked diurnal fluctuation')
            nrest.append('Segawa disease')
            continue

          if r in ['dup(10q) syndrome', 'Del(18p) Syndrome', 'Del(18q) Syndrome']:
            nrest.append(r)
            continue

          print("Failure to parse")
          print(r)
          print(orest)
          sys.exit()
        rest = nrest
        rest.append(name)
        rest = [r.strip() for r in list(set(rest))]
        for r in rest:
          r = str(r)
          if re.match(r'with +', r): continue
          if len(r) <= 1: continue
          ret[r] = ret.get(r, [])
          ret[r].append([str(name), str(url)])
      self.last_fetched = time.time()
    with open(local_path, 'w') as f:
      f.write(yaml.dump(ret))
    return ret


dd = DrugData()
dd.rare_diseases()
# pp(dd.rare_diseases())
# dd.update_drug_list()
# dd.fix_names()
dd.information()
# dd.repurpose()

# TODO: get indications, drug company
# https://www.google.com/search?q=site%3Awikipedia.com+bladder+cancer