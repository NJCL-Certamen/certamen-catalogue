# Certamen Catalogue

This project is designed to create a central repository for *Certamen* rounds in a format that can be read and used by other applications. Our aim is to facilitate any and all who want to explore the possibilities of combining *Certamen* with technology.

## Project Structure

### Questions Folder

The `questions/` folder holds the questions in YAML format (more on that below) and is divided first by tournament, then by year, then by level. Currently the file names follow a similar pattern (e.g. `njcl2019adv1.yaml`)

### Skills Folder

The `.github/skills/` folder holds AI skills that are useful for parsing question documents into YAML or for using YAML formatted questions for other purposes

#### convert-certamen-round-to-yaml skill

This skill has been used to convert most of the current YAML files in the repository. It works best with Gemini for Docs, since, among other things, Gemini seems to have the best handle on what text is bolded/italicized/underlined, which helps in marking certain text as Latin or a Title to preserve formatting.

### Scripts Folder

The `scripts/` folder will hold various scripts that can be used to create, manipulate, or use the YAML round files

## Certamen Round YAML format

```yaml
tournament: NJCL Certamen # the name of the tournament
year: 2022 # year the tournament took place
division: Advanced # division
round: Finals # Round 1, Round 2, Round 3, Semifinals, Finals
questions: # array of all the tossups
  - tossup:
      question: "More often than not, the contingent of moderators running this tournament dislikes challenges. Some moderators, however, enjoy a good challenge. Describe this challenge that has been given to all of this tournament’s moderators: <latin>Cōnāminī nūllīs quaestiōnibus extrāneīs ūtī!</latin>" # notice that Latin text is marked with the <latin></latin> pseudo-html tags to indicate that the text is Latin and should be displayed with some form of text decoration to show that (see below)
      answer: "TRY NOT TO USE EXTRA QUESTIONS (CHALLENGE) vel sim."
    boni: # array of bonus questions
      - question: "Now again describe this challenge straight from the moderators’ room. <latin>Cōnāminī haud nimium “Iuvencōs Russōs” haurīre!</latin>"
        answer: "TRY NOT TO DRINK TOO MANY RED BULLS (CHALLENGE) vel sim."
      - question: "Now again describe this final challenge, one that we almost fail every year: <latin>Cōnāminī ex harēnā nōn ēicī antequam certāmen fīniātur.</latin>"
        answer: "TRY NOT TO GET KICKED OUT OF THE ARENA / SAND / ROOM / THEATER / ETC. (BEFORE THE ROUND IS FINISHED CHALLENGE) vel sim"
```

### Pseudo-tags

The following pseudo-html tags are used to indicate that certain text needs decoration to distinguish it on the page

- `<latin></latin>` - indicates Latin or other ancient language text, which the moderator should not be pronouncing like English. In NJCL questions this type of text is **bolded**
- `<title></title>` - indicates text that is the title of a literary work. In NJCL questions titles are *italicized*
- `<emphasis></emphasis>` - indicates text that requires emphasis (or text that is the crucial part of a long and interpretive answer). In NJCL questions this type of text is usually <u>underlined</u>

## Issues

Is there an improvement to this project that you'd like to see? You can suggest improvements via the [Issues Tab](https://github.com/NJCL-Certamen/certamen-catalogue/issues) or you can take a look at [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines how to contribute the improvement yourself.
