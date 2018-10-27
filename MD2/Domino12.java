/**
 * This code is created as a homework 2 for "Modern programming technologies" course
 * at Latvian University.
 *
 * The main idea of the code below is to accept 1 integer argument, shuffle domino pack and
 * distribute dominos to players.
 *
 * @author Eduards Mukans em18044
 */

import java.util.ArrayList;
import java.util.Collections;


class Domino12 {
    private ArrayList<Kaulins> dominoList = new ArrayList<Kaulins>();
    private int playerCount;

    private final int DOMINO_COUNT_IN_PACK = 12;

    public Domino12(int Z) {
        this.playerCount = Z;
    }

    public static void main(String args[]) {
        int Z = Integer.parseInt(args[0]);

        Domino12 dominoPack = new Domino12(Z);
        dominoPack.generateDominoList();
        dominoPack.shuffleDomino();
        dominoPack.distributeToPlayers();
    }

    private void generateDominoList() {
        int skippedIndex = 0;
        boolean isFirst = true;

        for(int i = 0; i <= this.DOMINO_COUNT_IN_PACK; i++) {
            for(int j = 0; j <= this.DOMINO_COUNT_IN_PACK; j++) {
                if (!isFirst && j < skippedIndex) {
                    continue;
                }

                Kaulins domino = new Kaulins(i, j);

                this.dominoList.add(domino);
            }

            isFirst = false;
            skippedIndex++;
        }
    }

    private void shuffleDomino() {
        Collections.shuffle(this.dominoList);
    }

    private void distributeToPlayers() {
        int dominoCountForPlayer = this.dominoList.size() / this.playerCount;

        for (int i = 1; i <= this.playerCount; i++) {
            ArrayList<Kaulins> playerDomino = new ArrayList<Kaulins>(this.dominoList.subList(((i - 1) * dominoCountForPlayer), i * dominoCountForPlayer));

            System.out.printf("%d.speletajam ir: %s\n", i,  Domino12.dominoListToString(playerDomino));
        }
    }

    private static String dominoListToString(ArrayList<Kaulins> playerDomino) {
        String dominoString = "";

        for(Kaulins domino: playerDomino) {
            dominoString += domino.toString() + " ";
        }

        return dominoString;
    }
}

class Kaulins {
    private int pirmais_kv;
    private int otrais_kv;

    public Kaulins(int pirmais, int otrais) {
        pirmais_kv = pirmais;
        otrais_kv = otrais;
    }

    public String toString() {
        return pirmais_kv + "-" + otrais_kv;
    }
}
