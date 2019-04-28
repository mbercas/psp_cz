#!/usr/bin/env python3


from ufal.morphodita import *
from pathlib import Path
import sys

#dict_path = '/mnt/Users/manuel/projects/working/tools/dicts/czech-morfflex-pdt-161115/czech-morfflex-161115.dict'
dict_path = 'czech-morfflex-161115.dict'
#tagger_path = '/mnt/Users/manuel/projects/working/tools/dicts/czech-morfflex-pdt-161115/czech-morfflex-pdt-161115.tagger'
tagger_path = 'czech-morfflex-pdt-161115.tagger'

morpho = Morpho.load(dict_path)
if None == morpho:
    print("ERROR: Did not load the dictiorary")


text = "Hezké odpoledne, vážený pane předsedající, vážená vládo, kolegyně, kolegové. Nedá mi, abych nezareagoval na vystoupení pana předsedy Kováčika, který říkal, že jsme tu v historii měli různé počty. To je pravda. Ale ty počty se braly tak, aby vždy každá politická strana zvolená v Poslanecké sněmovně měla zastoupení v mandátovém a imunitním výboru. Máme za sebou sedm volebních období a ani jednou se nestalo, že by některý poslanecký klub neměl zastoupení v tomto výboru. A už máme jeden dobrý precedens z tohoto volebního období. V minulém volebním období jsme měli 15člennou volební komisi, a aby všechny strany měly zastoupení ve volební komisi, to znamená, aby se mohly vzájemně kontrolovat, když budou počítat hlasy, tak jsme před chvílí vzali na vědomí ustanovení 19členné volební komise. V tomto případě logicky vyšli ti, kteří mají nejvíc hlasů, vstříc těm, kteří mají nejméně hlasů. Tak jak je to logické u volební komise, tak je to logické i u mandátového a imunitního výboru. U všech jiných je to věc politické dohody a názory většiny. Tady, pokud projde návrh menší než 18, kterýkoliv, tak dva poslanecké kluby odřízne od informací. A i my ostatní, kteří budeme mít zastoupení v mandátovém a imunitním výboru, tak přece víme, že dostaneme jenom obecnou informaci od toho, co se ti členové výboru na tom jednání dozvědí. Nedostaneme konkrétní a nemůžeme to po nich ani chtít. Oni nám mohou jenom sdělit svůj názor a doporučit, jak postupovat, až budeme hlasovat o doporučení mandátového a imunitního výboru. Takže pokud jsme zřídili volební komisi tak, aby měly zastoupení logicky všechny poslanecké kluby, tak si myslím, že ve stejné logice bychom měli určit takový počet členů mandátového a imunitního výboru, aby tam opět měly zastoupení všechny poslanecké kluby. U ostatních výborů, a mluvila o tom i paní poslankyně Němcová, vlastně v zásadě neplatí tento argument. Protože tam jednak mohou chodit i z těch stran, které tam mají zastoupení, jiní poslanci, jednání jsou veřejná, záleží na aktivitě každého, zda tam vystoupí, nebo ne. Nepamatuji si případ, že by poslanec, který není členem výboru, nedostal slovo na jiném výboru. Myslím, že je to naprosto běžné, zdvořilé a že to bude pokračovat i v tomto volebním období."
    
# Load the lemmas
tagger = Tagger.load(tagger_path)
forms = Forms()
tokens = TokenRanges()
lemmas = TaggedLemmas()
lemmas_forms = TaggedLemmasForms()  

tokenizer = tagger.newTokenizer()
if tokenizer == None:
    print ("ERROR: could not open the tokenizer")
    sys.exit(-1)

# Tag
tokenizer.setText(text)

t = 0
while tokenizer.nextSentence(forms, tokens):
    tagger.tag(forms, lemmas)
    for i, (lemma,token) in enumerate(zip(lemmas,tokens)):
        print('{}{}<token lemma="{}" tag="{}">{}</token>{}'.format(
            text[t : token.start],
            "<sentence>" if i == 0 else "",
            lemma.lemma,
            lemma.tag,
            text[token.start : token.start + token.length],
            "</sentence>" if i + 1 == len(lemmas) else ""))
        t = token.start + token.length
