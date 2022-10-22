using System.IO;

using System.Text.RegularExpressions;


void FixIDS()
{
    string dir = @"C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\strategicregions";

    string[] files = Directory.GetFiles(dir, "*.txt");

    int id = 1;
    foreach (string file in files)
    {
        string content = File.ReadAllText(file);

        content = Regex.Replace(content, @"id=(\d+)", "id=" + id);
        content = Regex.Replace(content, @"STRATEGICREGION_(\d+)", "STRATEGICREGION_" + id);

        File.WriteAllText(file, content);

        string newfile = Regex.Replace(file, @"(\d+)-", id + "-");
        File.Move(file, newfile);
        id++;
    }
}