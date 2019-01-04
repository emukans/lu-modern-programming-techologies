# Tehniska dokumentācija. 
 
### Ietvaru izvēlē 
 
Šim projektam es izvelējos Django Framework. Es varu pamatot savu izvēli ar sekojošam cēloņiem: 
1. Django ORM ir plašas iespējas, ar kuras vienkāršo datu manipulācijas. Kā ari Django ORM ir iebūvēti stipri kešošanas algoritmi un lazy load iespējas kuras paātrina datubāzes pieprasījumus un datu izņemšanu. 
2. Django ir viegli veidot jaunus termināla komandas. 
3. Ir viegli kombinēt HTML un datus, kā arī ir daudz palīglīdzekļus HTML rakstīšanai. 
4. Django forms dod iespēju ģenerēt HTML formas, pārbaudīt un tīrīt datus. 
5. Iepriekšēja pieredze ar Python valodu un Django līdzīgos uzdevumos. 
 
### Lokālā uzstādīšanā 
 
Lokālai uzstādīšanai ir paņemts Docker un Docker Compose, jo man ir iepriekšējā pieredze Docker un bija iepriekš sagatavota Django Docker konfigurācija, 
kura ir pieejama [githubā](https://github.com/emukans/docker-django). 
 
### Aplikācijas darba gaita 
 
1. Tiek saņemti JSON faili vai no termināla, vai no Web interfeisa; 
2. Algoritms izej cauri visiem sanemtiem failiem; 
3. Notiek failu validācija. Ja tāda spēle jau eksistē datubāzē, tad algoritms tika pārtraukts un paradās kļūda. Spēle pārbaudās pēc datuma un komandu nosaukumiem; 
4. Pārsērs izej cauri visam JSON laukiem, apstrādā datus un veido modeļus. Pārsēšana notiek ar vienu transakciju. Tas nozīme, ja ir kļūda datos, tad jaunie ieraksti neparadās datubāzē un tos nevajag tīrīt; 
5. Kad lietotājs apskata statistikas tabulas, dati tiek ņemti no datubāzes; 
6. Visa gaita strādā iebūvēti kešošanas mehānismi, kuras saglabā pieprasītus datus un lapas Redis datubāze. 
