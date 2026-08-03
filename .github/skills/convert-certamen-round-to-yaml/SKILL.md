---
name: convert-certamen-round-to-yaml
description: Use this skill when converting a Certamen round document into a yaml file in the proper format for the Certamen Question Catalogue Project. This should cover various formatting in which you may find Certamen rounds, but may require further prompting in some cases.
---

# Convert Certamen Round to YAML Skill

## Elements of a Certamen Round

### Tournament

The name of the tournament in which the round took place. This should not include the year, which is a separate field, so that tournaments that occur yearly can be associated together. This can often be found in the header of the document or at the top of it, although sometimes it is not in the document and will need to be provided by the user

### Year

The year that the tournament took place. This should be found in the header of the file or at the top and will most often be formatted as a four-digit year

### Division

Most Certamen tournaments include multiple divisions for players of different experience. The most common divisions are "Advanced", "Intermediate", and "Novice", but some tournaments have other divisions such as "Middle School" or sometimes just "Level #" where # can be an integer from 1 to 5. This information is most often found in the header or at the top of the document

### Round

Certamen tournaments involve multiple rounds, most commonly "Round 1", "Round 2", "Round 3", and "Finals" but some tournaments include a "Semifinals" or rounds numbered higher than 3. This information is most commonly found in the header or at the top of the document

### Questions

The bulk of the document is made up of questions, most commonly 20 of them. A question consists of a "tossup" and at least one, but usually two, bonus questions, both tossup and bonus questions consist of a question and an answer. The tossup question is preceeded by the question number (sometimes preceeded by "TU" or "Tossup" or "Toss up") and a colon or period, while the bonus questions are preceded by B# or Bonus# where # is a positive integer indicating which bonus it is, followed by a colon or period. Answers are always somehow separated from the question, usually by some amount of whitespace and is often capitalized

#### Example

```plaintext
2:	According to some sources, when Hera became enraged at Zeus’s single-parent birth of Athena, Hera independently gave birth to what god, whom she hated and tossed out?
		HEPHAESTUS
B1:	In other versions, it was not Hephaestus that Hera bore, but what monster?	
		TYPH(A)ON / TYPHOS / TYPHOEÜS
B2:	During the Gigantomachy, what giant attempted to rape Hera, but was killed by Zeus’ thunderbolt and Heracles’ arrow?	PORPHYRION
```

This example would break down as follows:
```yaml
tossup:
  question: "According to some sources, when Hera became enraged at Zeus’s single-parent birth of Athena, Hera independently gave birth to what god, whom she hated and tossed out?"
  answer: "HEPHAESTUS"
boni:
  - question: In other versions, it was not Hephaestus that Hera bore, but what monster?
    answer: TYPH(A)ON / TYPHOS / TYPHOEÜS
  - question: During the Gigantomachy, what giant attempted to rape Hera, but was killed by Zeus’ thunderbolt and Heracles’ arrow?
    answer: PORPHYRION
```

## Text Decoration

In order to capture bolded, italicized, and underlined text in the YAML format, use the following pseudo html tags to indicate text that should be decorated
- `<latin></latin>` - used for Latin text. Most commonly Latin text will be bolded (in NJCL Certamen rounds Latin and only Latin will be bolded), but sometimes it will be italicized. Text that involves long vowels (ā ē ī ō ū) is likely Latin
- `<title></title>` - used to denote the title of a work of literature and is pretty much always italicized in the original document. Titles are often but not always also Latin
- `<emphasis></emphasis>` - used for other emphasized text, should be used for any decorated text that isn't Latin or a title, especially if it's underlined.
DO NOT USE any other html or pseudo-html tags or backticks. The three above tags should be the only means of displaying text formatting.

Important conversion rule: when turning a round document into YAML, preserve formatting tags from the source whenever they are present, and add the appropriate pseudo-tag whenever the source contains Latin text, a literary title, or emphasized text. Do not strip, simplify, or omit these tags during parsing or extraction. Before finishing a conversion, verify that the YAML contains `<latin>`, `<title>`, or `<emphasis>` around any text that should be marked. Pseudo-tags should not be doubled (`<latin>text</latin>` is not valid), nesting however is allowed (`<latin><emphasis>text</emphasis></latin>` is valid). If there are multiple words in a row that require pseudo-tags prefer wrapping the whole phrase in a single pseudo-tag rather than wrapping each word individually. For example, `<title><latin>Dē Officiīs Ministrōrum</latin></title>` is preferred to `<title><latin>Dē Officiīs Ministrōrum</latin></title>`. Any punctuation can be included inside the pseudo-tags if it allows for longer phrases to be wrapped in a single pseudo-tag.

## Output format

tournament: <Tournament>
year: <Year>
division: <Division>
round: <Round>
questions:
  - tossup:
      question: <tossup question>
      answer: <tossup answer>
    boni:
      - question: <bonus 1 question>
        answer: <bonus 1 answer>
      - question: <bonus 2 question>
        answer: <bonus 2 answer>

### Example

```yaml
tournament: NJCL Certamen
year: 2022
division: Advanced
round: Round 1
questions:
  - tossup:
      question: "What author’s <latin>libellus</latin> contains 116 poems in several styles from epyllion to epigram, which he humbly called <latin>nūgae</latin>?"
      answer: "(C. VALERIUS) CATULLUS"
    boni:
      - question: "To what man, an author in his own right, did Catullus dedicate his <latin>lepidum novum libellum</latin>?"
        answer: "(CORNELIUS) NEPOS"
      - question: "Cornelius Nepos’ history entitled <title>Chronica</title> was an ambitious project that aimed to recount all of history from creation to his own day. Into how many books was the <title>Chronica</title> divided?"
        answer: "THREE"
  - tossup:
      question: "Excluding pronouns, how many words from the following sentence are derived from Latin? “You will remember me for centuries.”"
      answer: "TWO"
    boni:
      - question: "Give the adjective and its meaning at the Latin root for one of those words."
        answer: "SEE BELOW"
      - question: "Give another adjective and its meaning at the Latin root of one of those words."
        answer: "(REMEMBER) <latin>MEMOR</latin>, MINDFUL (OF) / REMEMBERING; (CENTURIES) <latin>CENTUM</latin>, HUNDRED"
  - tossup:
      question: "Although it is not clear what role the screech-owl played in their punishment, what twin giants were tortured by being bound back-to-back on a column with snakes?"
      answer: "OTUS AND EPHIALTES // ALOADAE"
    boni:
      - question: "Who was their mother, who brought them up as children of Alöeus, her husband?"
        answer: "IPHIMED(E)IA"
      - question: "How did Iphimedeia conceive the twins by Poseidon?"
        answer: "POURING (SEA)WATER INTO HER LAP"
```

