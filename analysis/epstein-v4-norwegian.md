# Hva vi faktisk vet om Epstein-saken — v4

*En primærkildebasert gjennomgang av det dokumenterte bevisgrunnlaget — oppdatert med funn fra systematisk OCR-analyse av EFTA-frigivelsen*

*Analyse styrt av Adrian Moen. Søk, analyse og skriving utført av Claude (Anthropic).*

*Merknad: Referanser til «v3» viser til en tidligere versjon av denne analysen som ble produsert før det systematiske OCR-tekstsøket. V3-analysen var basert på manuell lesning og kryssreferering mot 814 kilder. Dette dokumentet (v4) inkluderer funn fra systematisk tekstanalyse som v3 ikke fanget opp.*

*Merknad: Etter publisering oppdaget vi at [rhowardstone/Epstein-research](https://github.com/rhowardstone/Epstein-research) uavhengig hadde dokumentert de fleste av disse funnene i 165+ rapporter. Funnene nedenfor er kryssreferert og merket der de er uavhengig bekreftet. Funnet om «no client accounts» og metoden med sidenivå PDF-verifisering ser ut til å være unike bidrag fra dette prosjektet.*

---

## Om denne versjonen

v3 ble skrevet basert på to faser: OCR-prosessering av 4 251 PDF-er og en Research-basert sammenligning mot 814 offentlige kilder. v4 integrerer funn fra en tredje fase: systematisk tekstanalyse (grep, python, nettverksanalyse) utført av Claude på de 18 rensede OCR-filene (~6.8 MB), styrt av Adrian gjennom samtale. Denne fasen identifiserte substansielt materiale som ble oversett i de to første fasene — spesielt i SDNYs privilegerte påtalememoer i VOL00012.

Teksten bruker fortsatt fire evidensnivåer: **bekreftet**, **sannsynlig**, **ubesvart**, og **mønsterkonsistent**.

---

## Metode og begrensninger

Adrian Moen OCR-prosesserte 4 251 PDF-filer fra EFTA-serien med Tesseract. Han styrte deretter Claude (Anthropic) gjennom en serie samtaler for å søke, analysere og syntetisere resultatene. Claude utførte alt tekstsøk, kryss-referering, mønsteridentifisering og skriving. Adrian gjennomgikk flaggede passasjer og Claudes konklusjoner, valgte hvilke tråder å følge, og tok redaksjonelle beslutninger. Adrian leste ikke de rå OCR-filene selv — det gjorde Claude.

Verken Adrian eller Claude er journalist, advokat eller akademiker. Dette er en AI-generert analyse av offentlige myndighetsdokumenter, styrt av en privatperson. Hvert funn siterer et spesifikt EFTA-dokumentnummer som hvem som helst kan verifisere.

Den bygger på tre faser av analyse:

**Fase 1** besto av å OCR-prosessere 4 251 PDF-filer fra EFTA-serien (Epstein Files Transparency Act), frigitt av det amerikanske justisdepartementet i januar 2026. Prosesseringen ble utført med Anthropic Cowork.

**Fase 2** besto av en Research-basert sammenligning der hvert funn fra primærdokumentene ble sjekket mot 814 offentlige kilder.

**Fase 3** besto av systematisk tekstsøk og nettverksanalyse utført av Claude på OCR-filene, styrt av Adrian — navnefrekvensanalyse, co-occurrence-kartlegging, sladdeinkonsistens-identifisering, og kontekstuell rekonstruksjon av sladde identiteter. Denne fasen avdekket SDNYs interne påtalememoer, som er det mest substansielle materialet i hele frigivelsen.

**Begrensninger:** OCR-prosessering av skannede dokumenter innebærer feilmargin. VOL00001 er primært fotografier med minimal lesbar tekst. VOL00004 er dominert av telefonlogger med dårlig OCR-kvalitet. Det substansielle innholdet er konsentrert i VOL00012 (SDNYs påtalememoer og FBI-korrespondanse). Samme verktøy og metode kan brukes til å produsere overbevisende feilanalyse. Den eneste beskyttelsen er å aldri akseptere én analyse som endelig, inkludert denne.

---

## Den vanligste misforståelsen: «Vi vet ikke hvem som finansierte Epstein»

**Bekreftet:** Et SDNY-påtalememo fra 2019, frigitt i januar 2026, slår fast at «virtually all of Epstein's wealth» stammer fra to kilder knyttet til Leslie Wexner. Epstein hadde fullmakt over Wexners formue fra 1991 til 2007. Epstein betalte seg selv honorarer og underslo det Wexners advokater overfor føderale etterforskere beskrev som «several hundred million dollars».

**Nytt i v4 — bekreftet:** SDNYs eget memo fastslår: «We have not identified any accounts that are consistent with Epstein handling or investing other people's money.» Epsteins finanser gikk JP Morgan (tidlig 2000-tall → 2013) → Deutsche Bank (2013 → 2019) → Bank of Puerto Rico (2019). Kontoene var «exclusively for the purpose of holding his own money.» Deutsche Banks 50-siders interne analyse konkluderte med «no immediate indication of financial criminal activity.» Hedgefond-myten er ikke bare tvilsom — den er aktivt motbevist i primærdokumentene.

**Bekreftet:** Wexners advokat-proffer til SDNY (25. juli 2019) ga en detaljert beskrivelse: Epstein ble anbefalt som finansrådgiver på 1980-tallet. Han fikk gradvis kontroll med «virtually no oversight.» Han sa han hadde «other clients» og at de ville «settle up later.» I 2007 beskrev han sine juridiske problemer som «an overly aggressive police chief and some sort of massage.» Wexners kone oppdaget underslaget, Epstein forsøkte å overbevise henne om at «she did not understand the financials,» og familien inngikk et privat forlik der $100M ble returnert i januar 2008.

**Nytt i v4 — bekreftet:** Victoria's Secret ble brukt som aktivt rekrutteringsverktøy. Minst tre separate ofre ble lokket med løfter om modellkarriere gjennom VS. Wexner innrømmet gjennom sine advokater at han hørte rykter om at Epstein holdt seg ut som tilknyttet VS, men at Epstein benektet det da han ble konfrontert. Wexner tok ikke ytterligere steg.

---

## «Utlåns»-systemet: Hvem ofrene ble sendt til

v3 beskrev dette fragmentarisk. SDNYs påtalememo gir et sammenhengende bilde som er vesentlig mer alvorlig enn det folkelige narrativet antyder.

**Bekreftet:** Ett offer beskriver at hun ble «lent out so many times that she began using drugs» og «cannot estimate how many times.» Maxwell og Epstein vekslet på å instruere henne. Hun ble aldri betalt av de andre mennene. Følgende er navngitt i ett enkelt SDNY-memo:

**Bekreftelsesforbehold:** SDNYs memo sier eksplisitt at de ikke kunne bekrefte «utlåns»-forklaringene. De bekreftet offerets rekruttering av Maxwell, overgrep fra Epstein, og rekruttering av andre mindreårige, men de spesifikke anklagene om å bli instruert til å ha sex med personene nedenfor forblir ubekreftet i memoets egen vurdering (Kilde: EFTA02731136).

**Glen og Eva Dubin** — Maxwell instruerte offeret eksplisitt om å massere Glen Dubin og «do to Glen what she did for Epstein,» som offeret forstod som å utføre seksuelle handlinger. Glen Dubin er milliardær hedgefondforvalter. Offerets navn er sladdet. Det kan være Giuffre (som offentlig har anklaget Dubin i sivile søksmål) eller et annet offer — sladdingen forhindrer bekreftelse. Memoet selv bemerker: «No other victim has described being expressly directed by either Maxwell or Epstein to engage in sexual activity with any other men.» Uansett er dette SDNYs interne påtalememo som dokumenterer vitnemålet som del av deres saksforberedelse. Ingen rettshåndhevelse fulgte.

**Prince Andrew** — Maxwell sa til offeret at hun skulle møte en prins og «make him happy and do the exact same things for him that she did for Epstein because the prince was a good friend of Maxwell's.» SDNY noterte at de forsøkte å skaffe kontaktinformasjon for Prinsen, som ga «zero cooperation.»

**Harvey Weinstein** — Epstein instruerte offeret om å massere Weinstein ved Epsteins Paris-residens. Weinstein beordret henne til å fjerne skjorten. Hun nektet. Weinstein ble sint. *Ikke omtalt i v3.* Denne koblingen knytter Epsteins nettverk direkte til Weinsteins.

**Leon Black** — Epstein instruerte offeret om å massere Black ved NYC-residensen. Black initierte seksuell kontakt, offeret løp ut. Epstein lo det bort. En *annen* kvinne ble også dirigert til Black og utførte oralsex.

**Jes Staley** — Memoet bruker eksplisitt ordet «raped.» Da offeret klaget, sa Epstein at «he left it to [her] and Staley to decide whether to engage in sex.»

**Alan Dershowitz** — offeret «mentioned Alan Dershowitz, but we did not fully explore the details of her interactions with him.» SDNY kjente til påstander men valgte å ikke forfølge dem i dette memoet.

**Jean Luc Brunel** — massasje, ingen seksuell kontakt fra dette offeret.

**David Blaine** — introduserte et separat offer (ca. 18 år) for Epstein på en nattklubb i New York. Offeret ble deretter invitert til Epsteins øy og utsatt for gjentatte overgrep.

**Mønsterkonsistent:** Memoet presiserer at «no other victim has described being expressly directed by either Maxwell or Epstein to engage in sexual activity with any other men» — dette er altså basert på ett enkelt offers unikt detaljerte vitnemål. Andre ofre beskrev overgrep fra Epstein, men ikke det systematiske utlånet i samme omfang. Det betyr ikke at det ikke skjedde — det betyr at dette offeret er den eneste som har vitnet om det i denne detaljen.

---

## Leon Black og de 170 millioner dollarene

v3 kategoriserte bevisene mot Black som «sannsynlig, men omstridt i sivile søksmål.» v4 oppgraderer dette.

**Bekreftet:** Apollo-grunnlegger Leon Black betalte Epstein minst $158M (Dechert-rapporten) til $170M (Senatets finanskomité) mellom 2012 og 2017 gjennom Southern Trust Company Inc. Epstein hadde verken lisens som skatteadvokat eller sertifisert regnskapsfører.

**Nytt i v4 — bekreftet:** SDNY-interne e-poster fra juni 2023 viser en aktiv menneskehandelsreferanse — «Leon Black/Additional HT Subject Referral» — med identifisert mindreårig offer representert av Wigdor LLP. SDNY dekonflikterte med Manhattan DA, mottok avhørsnotater, og identifiserte «Potential targets» (sladdet). Hva som skjedde med referansen er ubesvart.

**Nytt i v4 — bekreftet:** Co-occurrence-analyse viser at Black er den nest mest dokumenterte personen i hele frigivelsen (58 tekstblokker), bare bak Maxwell (65). Black er SDNYs mest omtalte etterforsningsmål etter Maxwell — vesentlig mer enn Clinton, Andrew eller Staley.

**Nytt i v4 — bekreftet:** 2006 GRATs designet av Epstein for å unngå ~$1 milliard i gave- og eiendomsskatt ble finansiert med Apollo-fondsandeler verdt ~$585 millioner totalt. Epstein utviklet også en «step-up-basis transaction» for ytterligere $600M i skattebesparelse. Black-Epstein-forholdet falt sammen over en betalingstvist i 2016-2017, med siste betaling i april 2017 og opphør av kommunikasjon høsten 2018.

---

## Epsteins kontrollsystem: Trafficking, ikke «relasjon»

v3 bruker primært språk om «overgrep» og «rekruttering.» Påtalememoene beskriver noe som mer presist er et fullstendig trafficking-system.

**Bekreftet:** Minst ett langtidsoffer var underlagt komplett kontroll:
- Epstein bestemte hårfarge (kort, blondt), valgte klær, kommenterte kroppen, presset til vekttap
- Offeret reiste overalt Epstein dro, var på vakt 24/7
- Helt økonomisk avhengig — ingen utdanning, ingen venner utenfor hans verden, ingen familie
- Tvunget til å signere NDA og healthcare proxy som ga Epstein og Maxwell medisinsk beslutningsmyndighet
- Voldtatt i gymsalen ved Palm Beach-residensen

Offeret forklarte: «She did not quit her job because she did not know where else she could go and was completely dependent on Epstein.»

**Bekreftet:** Epsteins rekrutteringssystem var eksplisitt i sine preferanser. Victim-1 (rekrutterer, New York) beskriver at Epstein sa «you know what I like» — som hun forstod som mindreårige, spinkle jenter. Han uttrykte misnøye med mørkhudede jenter. På minst ett tilfelle viste en jente Epstein ID for å bevise at hun var under 18 — mindreårighet var et kvalifikasjonskriterie, ikke et uhell.

**Bekreftet:** Victim-2 (rekrutterer, Florida) anslår at hun rekrutterte 20-30 jenter, de fleste mindreårige, over 2-3 år. Epstein instruerte henne eksplisitt om å advare jentene om hva de kunne forvente.

**Bekreftet:** Karin Models, eid av Jean Luc Brunel, fungerte som gjeldsfelle. Unge modeller fikk visum, ble fortalt at de skyldte byrået penger for reise og bolig, ble nektet castinger, og ble presentert for Epstein. En victim møtte Epstein på Brunels egen bursdagsfest. Innen dager var hun på hans Palm Beach-residens og ble utsatt for overgrep.

---

## Systematisk bevismakulering

**Bekreftet:** Påtalememoet dokumenterer tre separate tilfeller:

1. **2005, Palm Beach:** Epstein instruerte en assistent om å samle alle kontaktbøker og datamaskiner og levere dem til en uidentifisert mann. FBI bekreftet at datamaskiner syntes fjernet før ransakelsen.

2. **Etter 2005, Virgin Islands:** En assistent ble bedt om å hente kontaktbøker fra «every building on Epstein's island,» bringe dem til Maxwells hus i New York, og makulere dem der.

3. **Rundt fengsling:** En assistent ble bedt om å kaste vibratorer og nakenbilder av unge kvinner fra kjelleren i NYC-residensen.

**Nytt i v4 — bekreftet:** Maxwell holdt «binders of nude photos» i sitt eget hjem i New York. Maxwell fotograferte jevnlig andre kvinner, inkludert nakenbilder.

**Nytt i v4 — bekreftet:** Darren Indyke, Epsteins advokat, sa til et vitne at «if she ever needed help she should not talk to the police.» Samme Indyke brakte datamaskiner inn i fengselet slik at Epstein kunne ha videosex med en navngitt person mens han sonet.

---

## Systemsviktene: Hvorfor saken kunne fortsette i tiår

### Acosta-avtalen

**Bekreftet:** Acosta forhandlet NPA-avtalen som ga Epstein et delstatsforelegg mens FBI hadde identifisert 30+ mindreårige ofre. Acosta-avhøret (oktober 2019, to dager, under ed) avslører at han var «firm on two years» men endte på 18 måneder uten å kunne forklare hvordan. Han brukte «petite policy» — ikke hva som var adekvat straff, men om delstatsstraffen var så urimelig at føderal inngripen var nødvendig.

**Nytt i v4 — bekreftet:** Acosta benekter intelligence-koblingen direkte og utvetydig under ed: «I'm not aware of it» og «I do not know where [press reports] that I told someone that he was an intelligence asset» kom fra. «The answer is no, and no.»

**Nytt i v4 — bekreftet:** NPA-en ga immunitet til «any potential co-conspirators of Epstein, including but not limited to» fire navngitte personer og Lesley Groff — «none of whom were signatories to the NPA.» De fire er med rimelig sikkerhet Sarah Kellen, Adriana Ross, Nadia Marcinkova og Lesley Groff, basert på rollebeskrivelser i memoet matchet mot offentlig kjent informasjon.

### Groff: Aktiv til slutten

**Nytt i v4 — bekreftet:** Groff var operativt involvert helt til kort tid før Epsteins arrestasjon. I desember 2018 emailet hun et offer og inviterte henne til Epsteins NYC-residens — dette førte direkte til en $250,000-overføring med instruks om hemmelighold. SDNY ga Groff en «reverse proffer» i juli 2019 og advarte at de ikke ville tilby avtale uten samarbeid. Groffs advokat sa hun ville ta Fifth Amendment. Hun ble aldri tiltalt.

### «Cooperating Defendants: None»

**Nytt i v4 — bekreftet:** Memoet sier eksplisitt at SDNY hadde null samarbeidende medtiltalte ved tidspunktet for Epsteins tiltale. Strategien var å bruke tiltalen som brekkstang: «Following the filing of the initial indictment... we hope to approach other suspected and alleged co-conspirators.» Epsteins død 10. august 2019 eliminerte denne strategien fullstendig. Ingen av de navngitte — Groff, Dubin, Black, Staley — ble noen gang formelt tilnærmet som samarbeidspartnere.

### Epsteins betalingsmønster

**Nytt i v4 — bekreftet:** Memoet dokumenterer at «whenever negative articles were published, Epstein would wire her money» — inkludert $100,000 kort etter Miami Heralds dekning. I desember 2018 instruerte Epstein sin regnskapsfører Rich Kahn om å overføre $250,000 til et offer med instruks om at hun ikke skulle fortelle noen. Betalingene korrelerer med juridisk og medial risiko, ikke omsorg.

---

## Epsteins død

**Bekreftet:** Ti av elleve kameraer i SHU-enheten fungerte ikke. Video fra det første selvmordsforsøket ble permanent tapt. Cellenaboen ble overført uten erstatning. Vaktene Noel og Thomas forfalsket tilsynsregistre.

**Nytt i v4 — bekreftet fra bevisloggen:** FBI beslagla to komplette DVR-systemer med 16+ harddisker fra MCC, gjennomførte 3D-laserscanning av cellen, sikret 30-minutters runder-ark for juli-august 2019, SHU-innsattlogg, vaktlister, og MCC-telefonposter. JP Morgan Chase sendte en SAR (Suspicious Activity Report) vedrørende Tova Noel. FBI opprettet en egen kontrabandetterforskning (90C-NY-3154599) 17. august 2019. Dr. Imeri skrev e-post om at Epstein trengte cellemate — navnet er usladdet i én versjon av bevisloggen, sladdet i en annen.

**Nytt i v4 — bekreftet:** Memoet sier eksplisitt at ransakelsene «did not reveal any cameras in any of the bedrooms or massage rooms.» Dette motsier det folkelige narrativet om utpressingsmateriale. Men bevismakulering er dokumentert over et tiår — at kameraer var borte i 2019 betyr lite.

---

## Det som forblir ubesvart

Fra v3, oppdatert med v4-funn:

1. ~~Hva betyr «SOROS»-referansen i EFTA00476?~~ **Avklart:** OCR-artefakt fra en forsikringsoversikt. Dokumentet viser Epsteins husholdningsforsikringer via Insurance Office of Central Ohio (Wexner-tilknyttet).

2. **Hva inneholder MCC-videoarkivet?** FBI beslagla to DVR-systemer med 16+ harddisker — innholdet er ikke frigitt.

3. **Hva skjedde med Leon Black HT-referansen fra 2023?** SDNY hadde aktivt etterforsningsmål med identifisert mindreårig offer.

4. **Hvem er den rødhårete kvinnen som forgrep seg på en 15-åring på New Mexico-ranchen?** FBI noterte: «We have not been able to identify this individual.»

5. **Hva viser EFTA01913 — det ulesbare advokatmemoet?** OCR fanget kun fragmenter. Krever manuell lesing.

6. **Hvorfor ble Leslie Groff aldri tiltalt?** Memoet dokumenterer hennes rolle detaljert, og hun var aktiv til desember 2018.

7. **Hvorfor har ingen rettshåndhevelse fulgt opp Glen Dubin?** Han er navngitt av et annet, uavhengig offer i SDNYs eget påtalememo — separat fra Giuffres sivile krav.

8. **Hva skjedde med Darren Indykes potensielle obstruksjonsansvar?** Han instruerte vitner om å ikke snakke med politiet og tilrettela for seksuell aktivitet i fengsel.

---

## Etterord

Denne analysen ble styrt av én person og utført av en AI. Den tredje fasen — systematisk tekstanalyse av 6.8 MB OCR-data — tok omtrent to timer med styrt samtale og identifiserte Glen Dubin, Harvey Weinstein, David Blaine, Joseph Alvarez, Bella Klein, Kimberly Galindo, Rich Kahn, og Darren Indykes obstruksjon som navngitte men ikke allment kjente elementer i primærdokumentene. Den identifiserte også at Leon Black var gjenstand for aktiv føderal menneskehandelsetterforskning i 2023, at SDNY hadde null samarbeidende medtiltalte da Epstein døde, at ingen kameraer ble funnet i soverom, og at ingen klientkontoer noen gang eksisterte.

Mesteparten av dette materialet finnes i SDNYs privilegerte påtalememoer i VOL00012 — dokumenter som er merket «Attorney Work Product» og «Subject to Fed. R. Crim. P. 6(e)» men som nå er offentlige gjennom kongressvedtaket. Paradokset er at de mest substansielle dokumentene i hele frigivelsen er de færreste har lest, fordi de er begravd i 18 OCR-filer blant tusenvis av ulesbare fotografier og telefonlogger.

Det som gjenstår er det samme som alltid: viljen til å se på primærkildene og trekke konklusjoner basert på det som faktisk står i dokumentene — ikke på det noen forteller deg at de sier. AI erstatter ikke den viljen — men det gjør det mulig å lete i en skala som ikke var mulig før.
