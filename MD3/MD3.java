/**
 * This code is created as a homework 3 for "Modern programming technologies" course
 * at Latvian University.
 *
 * The main idea of the code below is to accept 2 integer argument, perform actions on big integers and display the result
 *
 * @author Eduards Mukans em18044
 */
 
import java.math.BigInteger;

// ================ Klasi MD3 modificet aizliegts!
public class MD3 {

    public static void main(String[] args)
    {
       LielsSkaitlis lielsSkaitlis1 = new LielsSkaitlis(args[0]);
       LielsSkaitlis lielsSkaitlis2 = new LielsSkaitlis(args[1]);

       lielsSkaitlis1.add(lielsSkaitlis2);
       lielsSkaitlis1.display();
       lielsSkaitlis1.reverse();
       lielsSkaitlis1.display();

       lielsSkaitlis2.sub(lielsSkaitlis1);
       lielsSkaitlis2.display();
       lielsSkaitlis2.reverse();
       lielsSkaitlis2.display();
    }
}
// ================ Klasi MD3 modificet aizliegts!


//Japapildina klase "LielsSkaitlis" ar nepieciesamo funcionalitati
class LielsSkaitlis {
    private String skaitlis;
    //Varat pievienot savus laukus, ja tas ir nepieciesams
    
    private BigInteger integerValue;
    private Boolean isInvalid = false;

    private final int MAX_INTEGER_LENGTH = 21;
    private final int MIN_INTEGER_LENGTH = 20;


    LielsSkaitlis(String str) {
        this.skaitlis = str;

        this.setIntegerValue(str);
    }

    public void add(LielsSkaitlis sk) {
        BigInteger result = this.getIntegerValue().add(sk.getIntegerValue());

        Boolean checkUpperBound = true;

        // In case both numbers are negative, we need to check lower bound instead of upper.
        if (this.isNegative() && sk.isNegative()) {
            checkUpperBound = false;
        }

        if (!this.isIntegerValid(result, checkUpperBound)) {
            this.skaitlis = this.getErrorMessage(checkUpperBound);
            this.isInvalid = true;
            return;
        }

        this.setIntegerValue(result);
        this.skaitlis = String.valueOf(result);
    }

    public void sub(LielsSkaitlis sk) {
        BigInteger result = this.getIntegerValue().subtract(sk.getIntegerValue());

        Boolean checkUpperBound = false;

        // In case first number is positive, but second is negative, we need to check upper bound instead of lower.
        if (!this.isNegative() && sk.isNegative()) {
            checkUpperBound = true;
        }

        if (!this.isIntegerValid(result, checkUpperBound)) {
            this.skaitlis = this.getErrorMessage(checkUpperBound);
            this.isInvalid = true;
            return;
        }

        this.setIntegerValue(result);
        this.skaitlis = String.valueOf(result);
    }

    public void reverse() {
        if (this.isInvalid) {
            return;
        }

        BigInteger result = new BigInteger(new StringBuffer(this.skaitlis.replace("-", "")).reverse().toString());

        if (this.isNegative()) {
            result = result.negate();
        }
        this.setIntegerValue(result);

        this.skaitlis = String.valueOf(result);
    }

    public BigInteger getIntegerValue() {
        return this.integerValue;
    }

    public void setIntegerValue(String str) {
        this.integerValue = new BigInteger(str);
    }

    public void setIntegerValue(BigInteger value) {
        this.integerValue = value;
    }

    public Boolean isNegative() {
        Boolean isNegative = false;

        if (this.getIntegerValue().compareTo(BigInteger.ZERO) == -1) {
            isNegative = true;
        }

        return isNegative;
    }

    private Boolean isIntegerValid(BigInteger value, Boolean checkUpperBound) {
        String result = String.valueOf(value);

        if (checkUpperBound) {
            return result.length() < this.MAX_INTEGER_LENGTH;
        }

        return result.length() < this.MIN_INTEGER_LENGTH;
    }

    private String getErrorMessage(Boolean isUpperBoundReached) {
        if (isUpperBoundReached) {
            return "SKAITLIS PAR LIELU";
        }

        return "SKAITLIS PAR MAZU";
    }

    //Varat pievienot savas metodes, ja tas ir nepieciesams


    // ================= Metodi display() modificet aizliegts!
    public void display() {System.out.println(skaitlis);}
}
