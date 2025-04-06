# Typy dokladov   
# Skladové operácie   
## BO — Počiatočný stav   
- `verified\_by`   
- `ended\_at`   
   
   
### 1. Generovaný   
- Document\_has\_products je vyplnený.   
   
Status: generovany   
   
### 2. Uzatvorený   
- `verified\_by` je označený autorizovaným používateľom.   
- ended\_at je nastavený.   
   
Status: uzatvoreny   
   
## MM — Presun v rámci skladu   
rozhodol som že bude sa tu registrovať len presun z bunky v bunku   
- `destinate\_cell`   
- `linked\_document` `MMO` (nepovinné)   
   
   
### 1. Vytvorený   
- Pridať `destinate\_cell` z `BMO` (ak existuje).   
- Používateľ pridáva produkty vrátane ich pozícií.   
   
Status: vytvoreny   
   
### 2. Uzatvorený   
- `destinate\_cell` je skontrolovaná (tovar presunutý).   
- ended\_at je nastavený.   
   
Status: uzatvoreny   
   
## FV — Presun mimo systému   
- `carrier`   
- `address\_id`   
- `post\_barcode`   
- `linked\_document` `FVO`   
   
   
### 1. Generovanie   
- `carrier`, `address\_id` a `linked\_document\_id` sú definované.   
- Používateľ pridáva produkty vrátane ich pozícií.   
   
Status: na\_realizaciu   
   
### 2. Spracováva sa   
- Document\_has\_products je pripravený (produkty vychystané).   
   
Status: spracovava\_sa   
   
### 3. Pripravený na expedíciu   
- post\_barcode je definovaný.   
   
Status: pripraveny   
   
### 4. Uzatvorený   
- Tovar je expedovaný.   
- ended\_at je nastavený.   
   
Status: uzatvoreny   
   
### A1. Stornovaný   
- Len pre manažéra.   
   
Status: storno   
   
## IC+/IC-/IP+/IP- — Výsledky čiastočnej/plnej inventúry (manko/prebytok)   
- `linked\_document` `ICO`   
- `verified\_by`   
- `ended\_at`   
   
   
### 1. Uzatvorený   
- Dokument sa vytvára automaticky.   
- Document\_has\_products obsahuje prebytky.   
   
Status: uzatvoreny   
   
## WM- — Odpis/prijem v rámci prevodu medzi skladmi   
- `linked\_document` `TRO`/ `FVO`   
- `ended\_at`   
   
   
### 1. Generovaný   
- Vytvára sa na odpísanie tovaru pri príprave operácie ( `TRO`/ `FVO`).   
- Document\_has\_products sa vypĺňa dopisovanými/prijatymi produktmi.   
   
Status: generovany   
   
### 2. Uzatvorený   
- Potvrdenie operácie (ended\_at).   
   
Status: uzatvoreny   
   
## NN+/NN- — Neplánovaný príjem/výdaj   
- `verified\_by`   
- `ended\_at`   
   
### 1. Generovaný   
- Document\_has\_products sa vypĺňa.   
   
Status: generovany   
### 2. Uzatvorený   
- Zodpovedný používateľ potvrdzuje (verified\_by, ended\_at).   
   
Status: uzatvoreny   
   
## PZ — Príjem z externého zdroja   
- `verified\_by`   
- `ended\_at`   
- `carrier` (Voliteľné)   
- `address\_id` (Voliteľné, adresa dodávateľa)   
   
   
### 1. Generovaný   
- Používateľ vytvára príjmový dokument.   
- Document\_has\_products sa vypĺňa prijímanými produktmi.   
   
Status: generovany   
   
### 2. Uzatvorený   
- `verified\_by` sa označí po kontrole a umiestnení tovaru.   
- ended\_at sa nastavi.   
   
Status: uzatvoreny   
   
## RW/US+/US- — Zmena stávu z dôvodu reklamácie alebo z iných dôvodov   
### 1. Uzatvorený   
- Document\_has\_products sa vypĺňa odpisovanými produktmi   
- Len pre zodpovednú osôbu   
   
Status: uzatvoreny   
   
## WZ — Vrátenie dodávateľovi   
- `carrier`   
- `address\_id`   
- `post\_barcode`   
- `verified\_by`   
- `ended\_at`   
   
   
### 1. Generovaný   
- Používateľ vytvára dokument vrátenia.   
- `carrier`, `address\_id` sú definované.   
- Document\_has\_products sa vypĺňa vracanými produktmi.   
   
Status: na\_realizaciu   
   
### 2. Pripravený na expedíciu   
- Produkty sú zozbierané.   
- post\_barcode je definovaný.   
   
Status: pripraveny   
   
### 3. Uzatvorený   
- Tovar bol skutočne odoslaný dodávateľovi.   
- `verified\_by` sa označí.   
- ended\_at sa nastavi.   
   
Status: uzatvoreny   
   
### A1. Stornovaný   
- Len pre manažéra.   
   
Status: storno   
   
## ZB — Zberateľský baliček (Inventúra)   
- `linked\_document` `ICO`/ `IPO`   
- `Users`   
- `verified\_by`   
- `ended\_at`   
   
   
### 1. Vytvorený   
- Vytvára sa v rámci ICO/IPO na pridelenie oblasti/produktov konkrétnemu zberačovi (Users).   
   
Status: vytvoreny   
   
### 2. Spracováva sa   
- Zberač (Users) zadáva skutočné zásoby (Document\_has\_products).   
   
Status: spracovava\_sa   
   
### 3. Uzatvorený   
- Zberač dokončil zadávanie údajov.   
- `ended\_at` sa nastavi.   
- Údaje sú pripravené na aktualizáciu ICO/IPO.   
   
Status: uzatvoreny   
   
# Externé úlohy   
Generovanie a uzatváranie len pre manažérov!   
   
## MMO — Príkaz na presun v rámci skladu   
- `priority`   
- `start\_at`   
- `ended\_at`   
- `required\_at`   
- `verified\_by`   
- `origin\_cell`   
- `destinate\_cell`   
- `Products.amount\_added`   
- `Users`   
   
   
### 1. Vytvorený   
- `priority`, `start\_at`, `required\_at`, `origin\_cell`, `destinate\_cell` a `Users` sú definované.   
- Document\_has\_products má všetky amount\_required.   
   
Status: vytvoreny   
   
### 2. Uzatvorený   
- Musí byť dokončený pomocou dokumentu `MM`.   
- `verified\_by` je označený manažérom.   
- ended\_at je nastavený.   
   
Status: uzatvoreny   
   
## ICO/IPO — Príkaz na čiastočnú/úplnú inventúru   
- `priority`   
- `start\_at`   
- `ended\_at`   
- `required\_at`   
- `verified\_by`   
- `Products.amount\_added`   
- `Users` (Zoznam používateľov na vykonanie)   
   
   
### 1. Generovanie   
- Sú definované polia `priority`, `start\_at`, `required\_at`, `Products`, `Users`.   
- Document\_has\_products má všetky amount\_required (očakávané množstvo).   
   
Status: vytvoreny   
   
### 2. Aktualizácia   
- Získanie údajov o skutočných zásobách z uzatvorených dokumentov ZB.   
   
Status: aktualizovany (alebo zostáva vytvoreny až do uzatvorenia)   
   
### 3. Uzatvorený   
- Manažér ( `verified\_by`) kontroluje dokument a rozdiely.   
- Generovanie dokumentov `IC+`/ `IP+` a `IC-`/ `IP-` podľa výsledkov.   
- ended\_at je nastavený.   
   
Status: uzatvoreny   
   
## TRO/FVO — Príkaz na presun medzi skladmi / mimo systému   
- `destinate\_warehouse` (pre TRO)   
- `priority`   
- `carrier`   
- `address\_id`   
- `start\_at`   
- `ended\_at`   
- `required\_at`   
- `Products.amount\_added`   
   
   
### 1. Vytvorenie   
- Sú definované `destinate\_warehouse` (pre `TRO`), `priority`, `carrier`, `address\_id`, `start\_at`, `required\_at`.   
- Document\_has\_products má všetky amount\_required.   
   
Status: vytvoreny   
   
### 2. Aktualizácia   
- Získanie informácií o odpise tovaru z nového dokumentu WM-.   
   
Status: aktualizovany (alebo zostáva vytvoreny až do uzatvorenia)   
   
### 3. Uzatvorený   
- ended\_at je nastavený (po potvrdení expedície/príjmu).   
   
Status: uzatvoreny   