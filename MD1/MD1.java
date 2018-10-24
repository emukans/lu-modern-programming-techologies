/**
 * This code is created as a homework 1 for "Modern programming technologies" course
 * at Latvian University.
 *
 * The main idea of the code below is to accept 2 integer arguments and draw a triangle of "+ "
 * symbols with spaces indentation.
 *
 * @author Eduards Mukans em18044
 */

class MD1 {

    int triangleLength;
    int globalIndentLength;

    final String SYMBOL = "+ ";
    final String RULER = "1234567890123456789012345678901234567890123456789012345678901234567890";

    MD1(int Z, int N) {
        this.triangleLength = Z;
        this.globalIndentLength = N;
    }

    private void draw() {
        String globalIndent = this.buildRepeatedString(this.globalIndentLength, " ");

        for (int i = 0; i <= this.triangleLength; i++) {
            String indent = this.buildRepeatedString((this.triangleLength - i), " ");
            String symbols = this.buildRepeatedString(i, this.SYMBOL);
            System.out.println(globalIndent + indent + symbols);
        }

        System.out.println(RULER);
    }

    public static void main(String args[]) {
        int Z = Integer.parseInt(args[0]);
        int N = Integer.parseInt(args[1]);

        if (Z < 0 || Z > 20 || N < 0 || N > 30) {
            System.out.println("DATI NAV KOREKTI!");
            return;
        }

        MD1 task = new MD1(Z, N);
        task.draw();
    }

    private String buildRepeatedString(int length, String symbol) {
        String indent = "";

        for (int i = 0; i < length; i++) {
            indent += symbol;
        }

        return indent;
    }
}
