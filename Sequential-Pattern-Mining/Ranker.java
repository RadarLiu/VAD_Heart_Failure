import java.io.*;
import java.util.*;

public class Ranker
{
    private static class Info
    {
        public String seq;
        public int sup;
        public Info(String seq, int sup)
        {
            this.seq = seq;
            this.sup = sup;
        }
    }

    public static void main(String[] args) throws Exception
    {
        ArrayList<Info> list = new ArrayList<Info>();
        //BufferedReader reader = new BufferedReader(new FileReader("spade_diagnose_final.txt"));
        BufferedReader reader = new BufferedReader(new FileReader("spade_diagnose_from_heart_to_death_final.txt"));
        String line = null;
        while ((line = reader.readLine()) != null)
        {
            String[] fields = line.split(" #SUP: ");
            list.add(new Info(fields[0], Integer.parseInt(fields[1])));
        }
        reader.close();
        Comparator<Info> order = new Comparator<Info>()
        {
            public int compare(Info i1, Info i2)
            {
                return i2.sup - i1.sup;
            }
        };
        Collections.sort(list, order);
        BufferedWriter writer = new BufferedWriter(new FileWriter("output.txt"));
        for (Info t : list)
        {
            //writer.write(t.seq + " #SUP: " + t.sup + "\n");
            writer.write(t.sup + " ");
        }
        writer.close();
    }
}
