import java.util.LinkedList;

public class tester {
    public static void main(String[] args) {
        LinkedList<Integer> h = new LinkedList<Integer>();
        h.add(0);
        h.add(1);
        h.add(2);
        h.add(3);
        h.add(4);
        h.add(5);
        h.add(6);
        h.add(7);
        for (Integer i : h) {
            System.out.println(i);
        }
    }
}