pqCLI
===
CLI for ProQuest library service.

## Installation
Clone from GIT:<br>
`git clone https://github.com/js-on/pqCLI.git`

Install required modules:<br>
`pip install -r requirements.txt`

*nix only:<br>
Add shebang to beginning of *proquest.py*<br>
Make file executable: `chmod +x `
<br><br>

## Usage
1. Store ProQuest username in *config.py*
2. Store name of your institution in *config.py*
3. Decide whether to use keyring or not
4. `./pqCLI` and enter creds / setup keyring<br>
4.1 if keyring is used, login will be performed automatically<br>
4.2 if keyring is not used, you have to login each time manually<br>
5. Enter docID from ProQuest item

hXXps://ebookcentral.proquest.com/lib/XYZ/detail.action?docID=**4568785**&query=%22Incident+Management%22%2C
<br><br>

## Commands
| command      | description                                                         |
| ------------ | ------------------------------------------------------------------- |
| q/quit       | Logout from current session and exit                                |
| h/help       | Print help based on command dict and referenced function docstrings |
| d/unregister | Remove credentials from keyring                                     |
<br>

## Styles
You can add custom styles and change the default one in *config.py*<br>
It works by adding a string with predefined placeholders. You can see a list of placeholders below.<br>
A working template would be: *"\$Autor$, \$Titel$ - \$Verlag$"*

### Placeholders
- \$Titel$
- \$Autor$
- \$Verlag$
- \$Erscheinungs- termin Print$
- \$Erscheinungs- termin E-book$
- \$Sprache$
- \$Druck ISBN$
- \$E-Book ISBN$
- \$Seiten$
- \$LC-Schlagwort$
- \$LC Call Number$
- \$Dewey-Dezimalnummer$
- \$BISAC Subject Headings$
- \$Dokumenttyp$